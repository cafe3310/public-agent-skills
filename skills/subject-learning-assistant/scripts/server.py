import sys
import json
import yaml
import os
import http.server
import socketserver

def extract_data_from_dir(kb_path):
    data = []
    files = []
    
    # Support memocli default directory structure
    if os.path.isdir(kb_path):
        entities_dir = os.path.join(kb_path, 'entities')
        search_dir = entities_dir if os.path.exists(entities_dir) else kb_path
        
        for f in os.listdir(search_dir):
            if f.endswith(('.yaml', '.yml', '.json', '.md')) and not f.startswith('.'):
                files.append(os.path.join(search_dir, f))
    elif os.path.isfile(kb_path):
        files = [kb_path]

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                if file.endswith('.json'):
                    content = json.load(f)
                    if isinstance(content, list): data.extend(content)
                elif file.endswith(('.yaml', '.yml')):
                    content = yaml.safe_load(f)
                    if isinstance(content, list): data.extend(content)
                elif file.endswith('.md'):
                    raw_text = f.read()
                    frontmatter = {}
                    body = raw_text
                    if raw_text.startswith('---'):
                        parts = raw_text.split('---', 2)
                        if len(parts) >= 3:
                            try: frontmatter = yaml.safe_load(parts[1]) or {}
                            except: pass
                            body = parts[2]
                    
                    name = os.path.basename(file).replace('.md', '')
                    entity_type = frontmatter.get('entity type', 'Unknown')
                    
                    obs = []
                    for line in body.split('\n'):
                        line = line.strip()
                        if line.startswith('- '): line = line[2:]
                        elif line.startswith('* '): line = line[2:]
                        # Clean up append-update literal \n rendering
                        line = line.replace('\\n', ' ')
                        if line and not line.startswith('<!--') and not line.startswith('#'):
                            obs.append(line)
                            
                    data.append({
                        "type": "entity",
                        "name": name,
                        "entityType": entity_type,
                        "observations": obs
                    })
                    
                    for key, val in frontmatter.items():
                        if key.startswith('relation as '):
                            rel_type = key.replace('relation as ', '')
                            targets = val if isinstance(val, list) else [t.strip() for t in str(val).split(',')]
                            for t in targets:
                                if t:
                                    data.append({
                                        "type": "relation",
                                        "from": name,
                                        "to": t.replace(' ', '-'),
                                        "relationType": rel_type
                                    })
        except Exception as e:
            print(f"Error reading {file}: {e}")

    nodes = []
    links = []
    subway_path = []
    active_plan = None
    
    for item in data:
        if item.get('type') == 'entity':
            name = item.get('name')
            entity_type = item.get('entityType')
            obs = item.get('observations', [])

            if entity_type in ['Learning Plan', '学习计划']:
                active_plan = item
            
            status = "pending"
            if any(o in ["Status: Completed", "Status: Learned", "User Feedback: Understood", "状态: 已完成", "状态: 已学习", "已掌握"] for o in obs) or any("Completed" in o for o in obs):
                status = "completed"
            elif any(o in ["Status: Active", "Status: In Progress", "状态: 正在介绍", "状态: 进行中", "当前节点"] for o in obs) or any("Current Node" in o for o in obs) or any("Active" in o for o in obs) or any("正在介绍" in o for o in obs):
                status = "active"
            
            normalized_type = entity_type
            if entity_type == '学习主题': normalized_type = 'Learning Subject'
            elif entity_type == '子主题': normalized_type = 'Topic'
            elif entity_type == '概念': normalized_type = 'Concept'
            
            nodes.append({
                "id": name,
                "label": name,
                "type": normalized_type,
                "status": status,
                "info": "<br>".join(obs[:8])
            })
            
        elif item.get('type') == 'relation':
            links.append({
                "source": item.get('from'),
                "target": item.get('to'),
                "type": item.get('relationType')
            })

    if active_plan:
        plan_obs = active_plan.get('observations', [])
        task_outline = []
        
        def get_list(prefix, observations):
            for o in observations:
                if o.startswith(prefix):
                    try:
                        val = o.split(": ", 1)[1]
                        if val.startswith('['):
                            return json.loads(val)
                    except: pass
            return []

        for o in plan_obs:
            if o.startswith('Task Outline: ') or o.startswith('任务大纲: '):
                try:
                    val = o.split(": ", 1)[1]
                    task_outline = json.loads(val)
                except: pass
        
        for topic_name in task_outline:
            st_status = "pending"
            for n in nodes:
                if n['id'] == topic_name.replace(' ', '-'):
                    st_status = n['status']
                    break
            
            concepts_in_st = []
            prefixes = [f'Topic-{topic_name}: ', f'子主题-{topic_name}: ']
            for pref in prefixes:
                found_list = get_list(pref, plan_obs)
                if found_list:
                    concepts_in_st = found_list
                    break
            
            group_concepts = []
            for c_name in concepts_in_st:
                c_status = "pending"
                for n in nodes:
                    if n['id'] == c_name.replace(' ', '-'):
                        c_status = n['status']
                        break
                group_concepts.append({"name": c_name, "status": c_status})
            
            subway_path.append({
                "topic": topic_name,
                "status": st_status,
                "concepts": group_concepts
            })

    nodes = [n for n in nodes if n['type'] not in ['guide', 'Current Learning Status', '当前学习状态', None]]

    return {
        "nodes": nodes,
        "links": links,
        "subway": subway_path
    }

def start_server(kb_path, port=8000):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/data':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                data = extract_data_from_dir(kb_path)
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                return
            elif self.path == '/' or self.path == '/index.html':
                self.path = '/index.html'
            return super().do_GET()

    os.chdir(script_dir)
    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f"Serving Dashboard at http://localhost:{port}")
        print(f"Monitoring Knowledge Base at: {kb_path}")
        httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <KB_DIR_OR_FILE> [port]")
        sys.exit(1)
    
    kb_p = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    start_server(kb_p, port)
