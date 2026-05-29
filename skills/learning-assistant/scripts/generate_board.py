import os
import re
import json
import glob
import sys

def parse_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    frontmatter = {}
    body = ""
    
    # Simple regex to extract frontmatter between --- and ---
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)
        for line in fm_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                frontmatter[k.strip()] = v.strip()
    else:
        body = content
        
    return frontmatter, body

def parse_chapters(body):
    chapters = {}
    current_chapter = None
    current_lines = []
    
    for line in body.splitlines():
        if line.strip().startswith('## '):
            if current_chapter:
                chapters[current_chapter] = "\n".join(current_lines).strip()
            current_chapter = line.strip().replace('## ', '').strip()
            current_lines = []
        elif current_chapter is not None:
            current_lines.append(line)
            
    if current_chapter:
        chapters[current_chapter] = "\n".join(current_lines).strip()
        
    return chapters

def main(kb_dir, template_path, output_path):
    entities_dir = os.path.join(kb_dir, "entities")
    if not os.path.exists(entities_dir):
        print(f"Error: {entities_dir} does not exist.")
        sys.exit(1)
        
    nodes = []
    links = []
    topics_map = {}
    
    # 0. Get current concept from state file
    current_concept = None
    state_path = os.path.join(entities_dir, "当前学习状态.md")
    if os.path.exists(state_path):
        _, state_body = parse_md(state_path)
        state_chapters = parse_chapters(state_body)
        current_concept = state_chapters.get("当前正在介绍概念", "无").strip()
        if current_concept == "无":
            current_concept = state_chapters.get("当前正在介绍的概念", "无").strip()
        
    # 1. Parse all files
    for filepath in glob.glob(os.path.join(entities_dir, "*.md")):
        filename = os.path.basename(filepath)
        entity_name = filename[:-3] # remove .md
        fm, body = parse_md(filepath)
        
        etype = fm.get('entity type', 'unknown')
        
        status = "pending"
        chapters = parse_chapters(body)
        
        if etype == "概念":
            # Normalize names to check if it's the active concept
            is_active = False
            if current_concept and current_concept != "无":
                curr_c_base = current_concept.split('-')[-1].strip()
                entity_base = entity_name.split('-')[-1].strip()
                if current_concept.strip() == entity_name.strip() or curr_c_base == entity_base:
                    is_active = True
            
            if is_active:
                status = "active"
            else:
                progress = chapters.get("学习过程整理", "无").strip()
                if progress and progress != "无" and progress != "":
                    status = "completed"
                else:
                    status = "pending"
            
        mapped_type = "Unknown"
        if etype == "学习主题": mapped_type = "Learning Subject"
        elif etype == "学习计划": mapped_type = "Topic"
        elif etype == "概念": mapped_type = "Concept"
        elif etype == "状态": mapped_type = "State"
        else: mapped_type = etype
            
        node = {
            "id": entity_name,
            "label": entity_name.split('-')[-1] if '-' in entity_name else entity_name,
            "type": mapped_type,
            "status": status,
            "info": body[:100] + "..." if len(body) > 100 else body,
            "original_name": entity_name
        }
        
        if mapped_type != "State" and mapped_type != "学习日志":
            nodes.append(node)
            
        # extract relations
        for k, v in fm.items():
            if k.startswith('relation as '):
                links.append({
                    "source": entity_name,
                    "target": v
                })
                
        if mapped_type == "Topic":
            topics_map[entity_name] = {
                "topic": node["label"],
                "original_name": entity_name,
                "status": "pending",
                "concepts": []
            }
            
    # 2. Build subway
    # associate concepts to topics
    for link in links:
        source = link["source"]
        target = link["target"]
        source_node = next((n for n in nodes if n["id"] == source), None)
        if source_node and source_node["type"] == "Concept" and target in topics_map:
            topics_map[target]["concepts"].append({
                "name": source_node["label"],
                "status": source_node["status"]
            })
            
    # determine topic status
    for topic_name, t_data in topics_map.items():
        concepts = t_data["concepts"]
        if not concepts:
            t_data["status"] = "pending"
            continue
            
        all_completed = all(c["status"] == "completed" for c in concepts)
        any_completed = any(c["status"] == "completed" for c in concepts)
        any_active = any(c["status"] == "active" for c in concepts)
        
        if all_completed:
            t_data["status"] = "completed"
        elif any_completed or any_active:
            t_data["status"] = "active"
        else:
            t_data["status"] = "pending"
            
        # update topic node status as well
        topic_node = next((n for n in nodes if n["id"] == topic_name), None)
        if topic_node:
            topic_node["status"] = t_data["status"]
            
    # 2.1 Build subjects map and group topics under subjects
    subjects_map = {}
    for node in nodes:
        if node["type"] == "Learning Subject":
            subjects_map[node["id"]] = {
                "subject": node["label"],
                "original_name": node["id"],
                "topics": []
            }
            
    for link in links:
        source = link["source"]
        target = link["target"]
        source_node = next((n for n in nodes if n["id"] == source), None)
        if source_node and source_node["type"] == "Topic" and target in subjects_map:
            t_data = topics_map.get(source)
            if t_data and t_data not in subjects_map[target]["topics"]:
                subjects_map[target]["topics"].append(t_data)
                
    subway = list(subjects_map.values())
    
    # 3. Add virtual Root node to pull all subjects and logs together
    root_node = {
        "id": "Root",
        "label": "学习主目录",
        "type": "Root",
        "status": "completed",
        "info": "虚构的知识库根节点，用于拉近和统一管理不同的学习主题与日志。",
        "original_name": "Root"
    }
    nodes.append(root_node)
    
    for node in nodes:
        if node["id"] != "Root" and node["type"] == "Learning Subject":
            links.append({
                "source": "Root",
                "target": node["id"]
            })
            
    data = {
        "nodes": nodes,
        "links": links,
        "subway": subway
    }
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
        
    final_html = template.replace('__INJECTED_DATA__', json.dumps(data))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"✅ 看板生成成功：{os.path.abspath(output_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_board.py <KB_DIR> [output_path.html]")
        sys.exit(1)
        
    kb_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "board.html"
    
    # determine script dir to find template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "..", "assets", "board_template.html")
    
    main(kb_dir, template_path, output_path)