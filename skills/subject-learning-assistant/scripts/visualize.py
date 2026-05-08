import sys
import json
import yaml
import os
import http.server
import socketserver
import threading
import time

def generate_viz(data_path, output_path):
    try:
        if data_path.endswith('.yaml') or data_path.endswith('.yml'):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        if not data:
            return

    except Exception as e:
        print(f"Error loading data: {e}")
        return

    nodes = []
    links = []
    logs = []
    subway_path = []
    active_plan = None
    
    # First pass: find entities and logs
    for item in data:
        if item.get('type') == 'entity':
            name = item.get('name')
            entity_type = item.get('entityType')
            obs = item.get('observations', [])
            
            if entity_type == '学习日志':
                logs.append({
                    "name": name,
                    "timestamp": next((o.split(": ")[1] for o in obs if o.startswith("时间戳")), ""),
                    "summary": next((o.split(": ")[1] for o in obs if o.startswith("摘要")), ""),
                    "obs": obs
                })
                continue

            if entity_type == '学习计划':
                active_plan = item
            
            # Status check for visualization
            status = "pending"
            if any(o in ["状态: 已完成", "状态: 已学习", "已掌握"] for o in obs) or any("用户反馈: 已理解" in o for o in obs):
                status = "completed"
            elif any(o in ["状态: 正在介绍", "状态: 进行中", "当前节点"] for o in obs) or any("正在介绍" in o for o in obs):
                status = "active"
            
            nodes.append({
                "id": name,
                "label": name,
                "type": entity_type,
                "status": status,
                "info": "<br>".join(obs[:8])
            })
            
        elif item.get('type') == 'relation':
            links.append({
                "source": item.get('from'),
                "target": item.get('to'),
                "type": item.get('relationType')
            })

    # Robust Subway Path Construction
    if active_plan:
        plan_obs = active_plan.get('observations', [])
        task_outline = []
        
        # Helper to extract list from observation string or list
        def get_list(prefix, observations):
            for o in observations:
                if o.startswith(prefix):
                    val = o.split(": ", 1)[1]
                    if val.startswith('['):
                        try: return json.loads(val)
                        except: pass
                    # If it's already a list (from YAML parser), it might be tricky in raw string form
                    # But if we are here, 'o' is a string. If the source was a YAML list, 
                    # the observations list might contain the list directly? 
                    # Let's check if the observation itself is a list (unlikely given split)
            return []

        # Find task outline
        for o in plan_obs:
            if o.startswith('任务大纲: '):
                val = o.split(": ", 1)[1]
                try: task_outline = json.loads(val)
                except: pass
        
        for sub_topic_name in task_outline:
            st_status = "pending"
            for n in nodes:
                if n['id'] == sub_topic_name:
                    st_status = n['status']
                    break
            
            concepts_in_st = []
            # Check for both "子主题-NAME: " and "任务节点-NAME: "
            prefixes = [f'子主题-{sub_topic_name}: ', f'任务节点-{sub_topic_name}: ']
            for pref in prefixes:
                found_list = get_list(pref, plan_obs)
                if found_list:
                    concepts_in_st = found_list
                    break
            
            group_concepts = []
            for c_name in concepts_in_st:
                c_status = "pending"
                for n in nodes:
                    if n['id'] == c_name:
                        c_status = n['status']
                        break
                group_concepts.append({"name": c_name, "status": c_status})
            
            subway_path.append({
                "sub_topic": sub_topic_name,
                "status": st_status,
                "concepts": group_concepts
            })

    # Sort logs by timestamp/name
    logs.sort(key=lambda x: (x['timestamp'], x['name']))

    # Filter out technical entities
    nodes = [n for n in nodes if n['type'] not in ['guide', '当前学习状态', None]]

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <title>Learning Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; display: flex; height: 100vh; background: #f4f7f6; color: #2c3e50; }
        #left-panel { flex: 3; position: relative; border-right: 1px solid #e0e0e0; background: #fff; }
        #mid-panel { width: 340px; border-right: 1px solid #e0e0e0; background: #fafafa; overflow-y: auto; padding: 25px; }
        #right-panel { width: 340px; overflow-y: auto; background: #fff; padding: 25px; box-shadow: inset 10px 0 15px -10px rgba(0,0,0,0.05); }
        
        /* Graph Styles */
        .node text { pointer-events: none; font-size: 11px; fill: #555; }
        .link { stroke: #d3d3d3; stroke-opacity: 0.5; stroke-width: 1.5px; }
        
        .tooltip {
            position: absolute; padding: 15px; background: white; border-radius: 12px;
            pointer-events: none; font-size: 12px; max-width: 300px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 1000; border: 1px solid #f0f0f0;
        }

        /* Subway Styles */
        .subway-container { position: relative; padding-left: 5px; }
        .subway-item { position: relative; margin-bottom: 25px; }
        .sub_topic-header { display: flex; align-items: center; margin-bottom: 12px; }
        .sub_topic-dot { 
            width: 16px; height: 16px; border-radius: 4px; background: #3498db; 
            margin-right: 12px; flex-shrink: 0; box-shadow: 0 3px 6px rgba(52, 152, 219, 0.3);
        }
        .sub_topic-label { font-size: 15px; font-weight: 700; color: #34495e; }
        .sub_topic-item.completed .sub_topic-dot { background: #2ecc71; box-shadow: 0 3px 6px rgba(46, 204, 113, 0.3); }
        .sub_topic-item.active .sub_topic-dot { 
            background: #f1c40f; border: 2px solid #e67e22; 
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 126, 34, 0.4); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(230, 126, 34, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 126, 34, 0); }
        }

        .concept-list { padding-left: 22px; border-left: 2px solid #eee; margin-left: 7px; }
        .concept-item { display: flex; align-items: center; margin-bottom: 10px; font-size: 13px; }
        .concept-dot { width: 10px; height: 10px; border-radius: 50%; background: #dfe6e9; margin-right: 12px; border: 2px solid #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .concept-item.completed .concept-dot { background: #2ecc71; }
        .concept-item.active .concept-dot { background: #f1c40f; border-color: #e67e22; }
        .concept-item.active .concept-label { font-weight: 600; color: #d35400; }
        .concept-item.pending .concept-label { color: #95a5a6; }

        /* Log Styles */
        .log-item { position: relative; padding-left: 25px; margin-bottom: 25px; border-left: 2px solid #ecf0f1; }
        .log-item::before { 
            content: ''; position: absolute; left: -7px; top: 2px; width: 12px; height: 12px; 
            background: #fff; border: 3px solid #3498db; border-radius: 50%; 
        }
        .log-time { color: #bdc3c7; font-size: 11px; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; }
        .log-summary { font-weight: 500; line-height: 1.5; color: #2c3e50; font-size: 13px; }
        
        h2 { font-size: 18px; font-weight: 800; margin-top: 0; padding-bottom: 15px; border-bottom: 2px solid #3498db; display: flex; align-items: center; }
        h2 span { margin-right: 12px; font-size: 24px; }

        .legend { position: absolute; bottom: 30px; left: 30px; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); font-size: 11px; }
        .legend-item { display: flex; align-items: center; margin-bottom: 8px; }
        .legend-color { width: 14px; height: 14px; margin-right: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div id="left-panel">
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #e74c3c; border-radius: 50%;"></div> 学习主题</div>
            <div class="legend-item"><div class="legend-color" style="background: #3498db; border-radius: 3px;"></div> 子主题 (Sub-topic)</div>
            <div class="legend-item"><div class="legend-color" style="background: #2ecc71; border-radius: 50%;"></div> 已掌握概念</div>
            <div class="legend-item"><div class="legend-color" style="background: #f1c40f; border: 2px solid #e67e22; border-radius: 50%;"></div> 正在学习</div>
        </div>
        <div id="viz"></div>
    </div>
    <div id="mid-panel">
        <h2><span>🗺️</span> 知识地图</h2>
        <div class="subway-container" id="subway-items"></div>
    </div>
    <div id="right-panel">
        <h2><span>📜</span> 学习日志</h2>
        <div id="log-container"></div>
    </div>
    <div class="tooltip" id="tooltip" style="opacity: 0;"></div>

    <script>
        const nodesData = %NODES%;
        const linksData = %LINKS%;
        const logsData = %LOGS%;
        const subwayData = %SUBWAY%;

        // Render Subway
        const subwayContainer = d3.select("#subway-items");
        subwayData.forEach(st => {
            const stItem = subwayContainer.append("div").attr("class", `subway-item sub_topic-item ${st.status}`);
            const header = stItem.append("div").attr("class", "sub_topic-header");
            header.append("div").attr("class", "sub_topic-dot");
            header.append("div").attr("class", "sub_topic-label").text(st.sub_topic);
            const conceptList = stItem.append("div").attr("class", "concept-list");
            st.concepts.forEach(c => {
                const cItem = conceptList.append("div").attr("class", `concept-item ${c.status}`);
                cItem.append("div").attr("class", "concept-dot");
                cItem.append("div").attr("class", "concept-label").text(c.name);
            });
        });

        // Render Logs
        const logContainer = d3.select("#log-container");
        [...logsData].reverse().forEach(log => {
            const item = logContainer.append("div").attr("class", "log-item");
            item.append("div").attr("class", "log-time").text(log.timestamp);
            item.append("div").attr("class", "log-summary").text(log.summary);
        });

        // Graph Initialization
        const panel = document.getElementById('left-panel');
        const width = panel.clientWidth, height = panel.clientHeight;
        const svg = d3.select("#viz").append("svg").attr("width", width).attr("height", height)
            .call(d3.zoom().scaleExtent([0.2, 3]).on("zoom", (e) => container.attr("transform", e.transform)))
            .append("g");
        const container = svg.append("g");

        const simulation = d3.forceSimulation(nodesData)
            .force("link", d3.forceLink(linksData).id(d => d.id).distance(d => d.source.type === '子主题' ? 80 : 120))
            .force("charge", d3.forceManyBody().strength(-500))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(50));

        const link = container.append("g").selectAll("line").data(linksData).enter().append("line").attr("class", "link");
        const node = container.append("g").selectAll("g").data(nodesData).enter().append("g").attr("class", "node-group")
            .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

        function getNodeColor(d) {
            if (d.type === "学习主题") return "#e74c3c";
            if (d.type === "子主题") return "#3498db";
            if (d.status === "completed") return "#2ecc71";
            if (d.status === "active") return "#f1c40f";
            return "#dfe6e9";
        }

        node.append("path")
            .attr("d", d => {
                if (d.type === "子主题") return d3.symbol().type(d3.symbolSquare).size(400)();
                if (d.type === "学习主题") return d3.symbol().type(d3.symbolCircle).size(1000)();
                return d3.symbol().type(d3.symbolCircle).size(250)();
            })
            .attr("fill", getNodeColor)
            .attr("stroke", d => d.status === "active" ? "#e67e22" : "#fff")
            .attr("stroke-width", d => d.status === "active" ? 4 : 2);

        node.append("text").attr("dx", 18).attr("dy", ".35em").text(d => d.label).style("font-weight", d => d.type === "子主题" ? "bold" : "normal");

        const tooltip = d3.select("#tooltip");
        node.on("mouseover", (event, d) => {
            tooltip.transition().duration(100).style("opacity", 1);
            tooltip.html(`<strong>${d.label}</strong> <span style="color:#95a5a6; font-size:10px;">• ${d.type}</span><hr style="margin:10px 0; border:0; border-top:1px solid #f0f0f0;">${d.info}`)
                .style("left", (event.pageX + 15) + "px").style("top", (event.pageY - 20) + "px");
        }).on("mouseout", () => tooltip.transition().duration(500).style("opacity", 0));

        simulation.on("tick", () => {
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
        function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
        function dragended(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }
        window.addEventListener('resize', () => {
            const w = panel.clientWidth, h = panel.clientHeight;
            d3.select("svg").attr("width", w).attr("height", h);
        });
    </script>
</body>
</html>
"
   .replace("%NODES%", json.dumps(nodes, ensure_ascii=False)) 
   .replace("%LINKS%", json.dumps(links, ensure_ascii=False)) 
   .replace("%LOGS%", json.dumps(logs, ensure_ascii=False)) 
   .replace("%SUBWAY%", json.dumps(subway_path, ensure_ascii=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Professional Dashboard generated at: {output_path}")

def start_server(data_path, output_path, port=8000):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                generate_viz(data_path, output_path)
            return super().do_GET()
    os.chdir(os.path.dirname(os.path.abspath(output_path)))
    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python visualize.py <input_data> <output_html> [--server]")
        sys.exit(1)
    d_p, o_p = sys.argv[1], sys.argv[2]
    if "--server" in sys.argv: start_server(d_p, o_p)
    else: generate_viz(d_p, o_p)
