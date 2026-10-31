import http.server
import socketserver
import json
import os
import re
import sys
from urllib.parse import urlparse

class ResearchDataHandler(http.server.SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code == 404:
            self.send_response(code)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            cwd = os.getcwd()
            try:
                files = os.listdir(cwd)
            except:
                files = ["无法列出目录内容"]
            error_html = f"""
            <html>
            <head><title>404 页面未找到</title></head>
            <body style="font-family: sans-serif; padding: 2rem; background: #f8f9fa;">
                <h1 style="color: #dc3545;">404 页面未找到</h1>
                <p>请求的路径 <code>{self.path}</code> 未找到。</p>
                <hr>
                <p><b>诊断信息：</b></p>
                <ul>
                    <li><b>当前工作目录：</b> <code>{cwd}</code></li>
                    <li><b>当前目录下的文件：</b> <code>{", ".join(files)}</code></li>
                    <li><b>研究目录 (RESEARCH_DIR)：</b> <code>{os.environ.get("RESEARCH_DIR", "未设置")}</code></li>
                </ul>
                <p>请确保您在包含 <code>index.html</code> 的目录下运行服务器。</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
        else:
            super().send_error(code, message, explain)

    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = self.gather_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif self.path == '/api/report':
            self.send_response(200)
            self.send_header('Content-type', 'text/markdown')
            self.end_headers()
            r_dir = os.environ.get("RESEARCH_DIR", ".")
            report_path = os.path.join(r_dir, "final_synthesis.md")
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write("报告尚未生成。".encode('utf-8'))
        else:
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()

    def gather_data(self):
        r_dir = os.environ.get("RESEARCH_DIR", ".")
        
        data = {
            "theme": "等待项目配置 (Awaiting Project Manifest...)",
            "graph": {"nodes": [], "links": []},
            "status_flow": [],
            "links": [],
            "global_stats": {
                "ongoing": 0,
                "completed": 0,
                "total_links": 0
            },
            "has_final_report": os.path.exists(os.path.join(r_dir, "final_synthesis.md"))
        }
        
        if not os.path.exists(r_dir):
            return data

        manifest_path = os.path.join(r_dir, "project_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                try:
                    manifest = json.load(f)
                    data["theme"] = manifest.get("project_name", "未知主题 (Unknown Theme)")
                except:
                    pass

        nodes = []
        links = []
        all_urls = []
        
        theme_id = "theme_node"
        nodes.append({"id": theme_id, "name": data["theme"], "category": 0, "symbolSize": 60, "is_completed": True})

        meth_id = "meth_node"
        nodes.append({"id": meth_id, "name": "领域方法论 (Domain Methodology)", "category": 1, "symbolSize": 45, "is_completed": True})
        links.append({"source": meth_id, "target": theme_id})

        def extract_links_from_file(filepath, task_name_display):
            if not os.path.exists(filepath): return
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            blocks = re.split(r'\n\s*\n', content)
            for i, block in enumerate(blocks):
                if not block.strip() or block.startswith('#'): continue
                
                # 1. Standard URL extraction
                found_urls = re.findall(r'(https?://[^\s\]\>]+)', block)
                
                # 2. Extract from [Source URL(s)] tags (handling domains and partial paths)
                tag_matches = re.findall(r'\[Source URLs?\]:?\s*(.*)', block, re.IGNORECASE)
                for tag_content in tag_matches:
                    # Strip any trailing markdown or metadata tags starting with [
                    clean_content = re.split(r'\[', tag_content)[0].strip()
                    # Split by semicolon or look inside parentheses
                    parts = re.split(r'[;()]', clean_content)
                    for p in parts:
                        # Remove any remaining brackets or artifacts from the potential URL
                        p = p.replace('[', '').replace(']', '').replace('*', '').strip().lower()
                        # Simple domain/path heuristic
                        if '.' in p and not p.startswith('http') and len(p) > 3:
                            # Avoid picking up dates or version numbers
                            if not re.match(r'^\d+\.\d+$', p):
                                normalized = "https://" + p
                                if normalized not in found_urls:
                                    found_urls.append(normalized)

                for u in found_urls:
                    try:
                        if u not in [l['url'] for l in all_urls]:
                            parsed = urlparse(u)
                            domain = parsed.netloc or parsed.path.split('/')[0]
                            # Strip tags
                            snippet = re.sub(r'\[Source URL[^]]*\]', '', block, flags=re.IGNORECASE)
                            snippet = re.sub(r'\[Data Precision[^]]*\]', '', snippet, flags=re.IGNORECASE)
                            # Strip the URL itself from the snippet to avoid redundancy
                            snippet = snippet.replace(u, '')
                            # Also strip bare versions of the URL if they exist
                            bare_u = u.replace('https://', '').replace('http://', '')
                            snippet = snippet.replace(bare_u, '')
                            # Clean up formatting
                            snippet = snippet.replace('*', '').replace('-', '').replace('#', '').strip()
                            
                            snippet = snippet[:100] + "..." if len(snippet) > 100 else snippet
                            all_urls.append({"url": u, "domain": domain, "task": task_name_display, "snippet": snippet})
                    except ValueError:
                        continue # Skip malformed URLs
                
                info_text = re.sub(r'\[Source URL[^]]*\]', '', block)
                info_text = re.sub(r'\[Data Precision[^]]*\]', '', info_text)
                info_text = info_text.replace('*', '').replace('-', '').strip()
                if info_text and filepath.endswith("knowledge_fragments.md"):
                    short_text = info_text[:35] + "..." if len(info_text) > 35 else info_text
                    info_id = f"info_{filepath}_{i}"
                    nodes.append({"id": info_id, "name": short_text, "category": 3, "symbolSize": 15, "is_completed": True})

        # Extract from initial context
        extract_links_from_file(os.path.join(r_dir, "initial_context.md"), "初始搜索 (Initial Search)")
        
        try: items = os.listdir(r_dir)
        except: items = []

        ongoing_count = 0
        completed_count = 0

        for item in items:
            task_path = os.path.join(r_dir, item)
            if os.path.isdir(task_path) and item.startswith("task_"):
                task_name = item
                spec_path = os.path.join(task_path, "task_spec.json")
                if os.path.exists(spec_path):
                    with open(spec_path, 'r', encoding='utf-8') as f:
                        try:
                            spec = json.load(f)
                            task_name = spec.get("task_name", task_name)
                        except: pass
                
                status_path = os.path.join(task_path, "status.txt")
                is_completed = False
                if os.path.exists(status_path):
                    with open(status_path, 'r', encoding='utf-8') as f:
                        if 'Completed' in f.read():
                            is_completed = True
                
                if item == "task_0_domain_methodology":
                    is_completed = True

                if is_completed:
                    completed_count += 1
                else:
                    ongoing_count += 1
                
                topic_id = f"topic_{item}"
                nodes.append({"id": topic_id, "name": task_name, "category": 2, "symbolSize": 30, "is_completed": is_completed})
                
                if item == "task_0_domain_methodology":
                    links.append({"source": topic_id, "target": theme_id})
                else:
                    links.append({"source": topic_id, "target": meth_id})

                frag_path = os.path.join(task_path, "knowledge_fragments.md")
                if os.path.exists(frag_path):
                    prev_node_count = len(nodes)
                    extract_links_from_file(frag_path, task_name)
                    for n in nodes[prev_node_count:]:
                        links.append({"source": n["id"], "target": topic_id})

        data["graph"]["nodes"] = nodes
        data["graph"]["links"] = links
        data["links"] = all_urls
        data["global_stats"]["ongoing"] = ongoing_count
        data["global_stats"]["completed"] = completed_count
        data["global_stats"]["total_links"] = len(all_urls)

        log_path = os.path.join(r_dir, "main_log.md")
        flow = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_section = "Init"
                section_details = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('## '):
                        if section_details:
                            flow.append({"step": current_section, "details": section_details})
                        current_section = line.strip('# ')
                        section_details = []
                    elif line.startswith('- '):
                        clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line.strip('- ').strip())
                        clean_line = re.sub(r'`(.*?)`', r'<code style="background:#e9ecef;padding:2px 4px;border-radius:4px;font-size:0.85em">\1</code>', clean_line)
                        section_details.append(clean_line)
                if section_details or current_section != "Init":
                    flow.append({"step": current_section, "details": section_details})
        data["status_flow"] = flow

        return data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.environ["RESEARCH_DIR"] = os.path.abspath(sys.argv[1])
    else:
        print("用法: python server.py <path_to_research_workspace>")
        sys.exit(1)
        
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True
    
    # Change working directory to the directory containing server.py so static files are served correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), ResearchDataHandler) as httpd:
        httpd.serve_forever()
