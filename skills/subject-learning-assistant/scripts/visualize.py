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
    
    # First pass: find entities, logs and the active plan
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
                # Simple logic to find the active plan (the one includes the current concept or just the latest)
                active_plan = item
            
            # Status check for visualization
            status = "pending"
            if any("已完成" in o or "用户反馈: 已理解" in o for o in obs):
                status = "completed"
            elif any("当前节点" in o or "正在介绍" in o for o in obs) or any("状态: 正在介绍" in o for o in obs):
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

    # Construct Subway Path from active plan
    if active_plan:
        obs = active_plan.get('observations', [])
        task_outline = []
        for o in obs:
            if o.startswith('任务大纲: '):
                try:
                    task_outline = json.loads(o.split(": ", 1)[1])
                except: pass
        
        for node_name in task_outline:
            concepts = []
            for o in obs:
                if o.startswith(f'任务节点-{node_name}: '):
                    try:
                        concepts = json.loads(o.split(": ", 1)[1])
                    except: pass
            
            for c_name in concepts:
                # Find status of this concept
                c_status = "pending"
                for n in nodes:
                    if n['id'] == c_name:
                        c_status = n['status']
                        break
                subway_path.append({"name": c_name, "status": c_status, "node": node_name})

    # Sort logs
    logs.sort(key=lambda x: (x['timestamp'], x['name']))

    # Filter out guides
    nodes = [n for n in nodes if n['type'] not in ['guide', None]]

    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <title>Subject Learning Assistant - Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; display: flex; height: 100vh; background: #f0f2f5; color: #333; }
        #left-panel { flex: 2; position: relative; border-right: 1px solid #ddd; background: #fff; }
        #mid-panel { width: 300px; border-right: 1px solid #ddd; background: #fcfcfc; overflow-y: auto; padding: 20px; }
        #right-panel { width: 320px; overflow-y: auto; background: #fafafa; padding: 20px; }
        
        .node { stroke: #fff; stroke-width: 1.5px; cursor: pointer; }
        .node text { pointer-events: none; font-size: 11px; fill: #444; font-weight: 500; }
        .link { stroke: #ccc; stroke-opacity: 0.4; stroke-width: 1.2px; fill: none; }
        
        .tooltip {
            position: absolute;
            padding: 12px;
            background: rgba(255,255,255,0.95);
            border: 1px solid #eee;
            border-radius: 8px;
            pointer-events: none;
            font-size: 12px;
            max-width: 280px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
        }

        /* Subway Style */
        .subway-container { position: relative; padding-left: 30px; margin-top: 20px; }
        .subway-line { position: absolute; left: 37px; top: 0; bottom: 0; width: 4px; background: #ddd; z-index: 1; }
        .subway-item { position: relative; margin-bottom: 25px; z-index: 2; display: flex; align-items: center; }
        .subway-dot { 
            width: 18px; height: 18px; border-radius: 50%; background: #bdc3c7; border: 3px solid #fff; 
            margin-right: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-shrink: 0;
        }
        .subway-item.completed .subway-dot { background: #2ecc71; }
        .subway-item.active .subway-dot { background: #f1c40f; border-color: #e67e22; transform: scale(1.2); }
        .subway-label { font-size: 13px; font-weight: 500; }
        .subway-item.active .subway-label { color: #e67e22; font-weight: bold; }
        .subway-item.pending .subway-label { color: #95a5a6; }
        .subway-node-tag { font-size: 9px; color: #888; display: block; margin-top: 2px; }

        /* Log Style */
        .log-item { position: relative; padding-left: 20px; margin-bottom: 20px; border-left: 2px solid #3498db; font-size: 12px; }
        .log-item::before { content: ''; position: absolute; left: -6px; top: 0; width: 10px; height: 10px; background: #3498db; border-radius: 50%; }
        .log-time { color: #888; font-size: 10px; margin-bottom: 4px; }
        .log-summary { font-weight: bold; color: #2c3e50; }
        
        h2 { font-size: 15px; color: #333; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 8px; display: flex; align-items: center; }
        h2 span { margin-right: 8px; }

        .legend { position: absolute; bottom: 20px; left: 20px; background: rgba(255,255,255,0.9); padding: 10px; border: 1px solid #eee; border-radius: 6px; font-size: 10px; }
        .legend-item { display: flex; align-items: center; margin-bottom: 4px; }
        .legend-color { width: 10px; height: 10px; margin-right: 6px; border-radius: 50%; }
    </style>
</head>
<body>
    <div id="left-panel">
        <div class="legend">
            <div class="legend-item"><div class="legend-color" style="background: #e74c3c;"></div> 主题</div>
            <div class="legend-item"><div class="legend-color" style="background: #3498db;"></div> 计划</div>
            <div class="legend-item"><div class="legend-color" style="background: #2ecc71;"></div> 已掌握</div>
            <div class="legend-item"><div class="legend-color" style="background: #f1c40f; border: 2px solid #e67e22;"></div> 正在介绍</div>
            <div class="legend-item"><div class="legend-color" style="background: #bdc3c7;"></div> 待学习</div>
        </div>
        <div id="viz"></div>
    </div>
    <div id="mid-panel">
        <h2><span>🗺️</span> 知识路径 (Subway Map)</h2>
        <div class="subway-container">
            <div class="subway-line"></div>
            <div id="subway-items"></div>
        </div>
    </div>
    <div id="right-panel">
        <h2><span>📜</span> 学习历程 (Flow)</h2>
        <div id="log-container"></div>
    </div>
    <div class="tooltip" id="tooltip" style="opacity: 0;"></div>

    <script>
        const nodesData = %NODES%;
        const linksData = %LINKS%;
        const logsData = %LOGS%;
        const subwayData = %SUBWAY%;

        // Render Subway Map
        const subwayContainer = d3.select("#subway-items");
        subwayData.forEach(d => {
            const item = subwayContainer.append("div")
                .attr("class", `subway-item ${d.status}`);
            item.append("div").attr("class", "subway-dot");
            const labelGroup = item.append("div");
            labelGroup.append("div").attr("class", "subway-label").text(d.name);
            labelGroup.append("div").attr("class", "subway-node-tag").text(d.node);
        });

        // Render Logs
        const logContainer = d3.select("#log-container");
        logsData.reverse().forEach(log => {
            const item = logContainer.append("div").attr("class", "log-item");
            item.append("div").attr("class", "log-time").text(log.timestamp);
            item.append("div").attr("class", "log-summary").text(log.summary);
        });

        const width = document.getElementById('left-panel').clientWidth;
        const height = document.getElementById('left-panel').clientHeight;

        const svg = d3.select("#viz").append("svg").attr("width", width).attr("height", height)
            .call(d3.zoom().on("zoom", (event) => container.attr("transform", event.transform)))
            .append("g");

        const container = svg.append("g");
        const simulation = d3.forceSimulation(nodesData)
            .force("link", d3.forceLink(linksData).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-350))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(40));

        const link = container.append("g").selectAll("line").data(linksData).enter().append("line").attr("class", "link");
        const node = container.append("g").selectAll("g").data(nodesData).enter().append("g").attr("class", "node-group")
            .call(d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended));

        function getNodeColor(d) {
            if (d.type === "学习主题") return "#e74c3c";
            if (d.type === "学习计划") return "#3498db";
            if (d.status === "completed") return "#2ecc71";
            if (d.status === "active") return "#f1c40f";
            return "#bdc3c7";
        }

        node.append("circle").attr("r", d => d.type === "学习主题" ? 14 : (d.type === "学习计划" ? 10 : 7))
            .attr("fill", getNodeColor).attr("stroke", d => d.status === "active" ? "#e67e22" : "#fff").attr("stroke-width", d => d.status === "active" ? 3 : 1.5);
        node.append("text").attr("dx", 14).attr("dy", ".35em").text(d => d.label);

        const tooltip = d3.select("#tooltip");
        node.on("mouseover", (event, d) => {
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`<strong>${d.label}</strong> <span style="font-size:10px; color:#666">[${d.type}]</span><br><hr style="border:0; border-top:1px solid #eee; margin:8px 0;">${d.info}`)
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
            const w = document.getElementById('left-panel').clientWidth;
            const h = document.getElementById('left-panel').clientHeight;
            if (d3.select("svg").node()) d3.select("svg").attr("width", w).attr("height", h);
        });
    </script>
</body>
</html>
"""
    
    html = html_template.replace("%NODES%", json.dumps(nodes, ensure_ascii=False)) \
                        .replace("%LINKS%", json.dumps(links, ensure_ascii=False)) \
                        .replace("%LOGS%", json.dumps(logs, ensure_ascii=False)) \
                        .replace("%SUBWAY%", json.dumps(subway_path, ensure_ascii=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Subway visualization generated at: {output_path}")

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
    
    data_p = sys.argv[1]
    out_p = sys.argv[2]
    if "--server" in sys.argv:
        start_server(data_p, out_p)
    else:
        generate_viz(data_p, out_p)
