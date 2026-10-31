#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compile_mesh_dashboard.py / build_mesh_dashboard.py
AOP 需求架构全景 Dashboard 离线 HTML 网页全量编译生成脚本

加回「详情」按钮与三大交互完美协同 Solution:
  1. 卡片 Hover 动作区恢复「置顶」与「详情」两个按钮
  2. 点击卡片主体空白处：锁定保持高亮
  3. 点击「详情」按钮：显式打开 Markdown 全量文档与 Base64 SVG 预览 Modal 弹窗
  4. 点击「置顶」按钮：显式触发关联卡片联动置顶
"""

import os
import re
import json
import sys
import base64
import argparse
import subprocess
from pathlib import Path

# 导入提取与审计模块
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import extract_and_audit_mesh as audit_engine
except ImportError:
    audit_engine = None

def get_git_commit_hash(base_dir):
    """尝试获取当前目录或上层 Vault 的 short git commit hash"""
    current = os.path.abspath(base_dir)
    for _ in range(4):
        if os.path.exists(os.path.join(current, ".git")):
            try:
                res = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=current,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=3
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return ""

def get_clean_title(filename):
    name = filename.replace(".md", "")
    parts = name.split("-", 1)
    if len(parts) > 1:
        return parts[0], parts[1]
    return parts[0], name

def scan_svg_attachments_b64(base_dir):
    """扫描多层 _attachments 目录下的 SVG 文件内容并全量转码为 Base64 Data URI"""
    svg_map = {}
    possible_dirs = [
        os.path.join(base_dir, "_attachments"),
        os.path.join(base_dir, "..", "_attachments"),
        os.path.join(base_dir, "..", "..", "_attachments"),
        os.path.join(base_dir, "..", "..", "..", "_attachments"),
    ]
    for attach_dir in possible_dirs:
        attach_dir = os.path.abspath(attach_dir)
        if os.path.exists(attach_dir):
            for root, dirs, files in os.walk(attach_dir):
                for f in files:
                    if f.endswith(".svg"):
                        fpath = os.path.join(root, f)
                        try:
                            with open(fpath, "rb") as fp:
                                raw_bytes = fp.read()
                                b64_str = base64.b64encode(raw_bytes).decode("utf-8")
                                svg_map[f] = f"data:image/svg+xml;base64,{b64_str}"
                        except Exception:
                            pass
    return svg_map

def find_md_files(target_dir, root_dir, prefix):
    """查找特定前缀的 md 文件"""
    search_path = target_dir if target_dir and os.path.exists(target_dir) else root_dir
    results = []
    if not search_path or not os.path.exists(search_path):
        return results
    
    path_obj = Path(search_path)
    if path_obj.is_file():
        if path_obj.name.startswith(prefix) and path_obj.name.endswith(".md"):
            results.append(path_obj)
        return results

    for r, d, files in os.walk(search_path):
        for f in files:
            if f.startswith(prefix) and f.endswith(".md"):
                results.append(Path(r) / f)
    return sorted(results)

def compile_dashboard(root_dir, layer1_dir=None, layer2_dir=None, layer3_dir=None, layer4_dir=None, output_html_path=None):
    base_dir = os.path.abspath(root_dir)
    project_name = os.path.basename(base_dir)
    
    d10_dir = os.path.join(base_dir, "项目规划/D10-故事和叙事")
    d20_dir = os.path.join(base_dir, "项目规划/D20-目标与重点")
    d30_dir = os.path.join(base_dir, "项目规划/D30-主功能分类(按aop)")
    d40_dir = os.path.join(base_dir, "项目规划/D40-需求Tickets")
    
    attach_dir = os.path.join(base_dir, "_attachments")
    svg_db = scan_svg_attachments_b64(base_dir)

    full_text_db = {}
    
    # 1. 查找各层文件
    l1_files = find_md_files(layer1_dir or d10_dir, base_dir, "D1")
    l2_files = find_md_files(layer2_dir or d20_dir, base_dir, "D2")
    l3_files = find_md_files(layer3_dir or d30_dir, base_dir, "D3")
    l4_files = find_md_files(layer4_dir or d40_dir, base_dir, "D4")

    # 2. 解析 D10 叙事
    d10_cards = []
    for fpath in l1_files:
        f = fpath.name
        parts = f.replace(".md", "").split("-")
        cid = parts[0] + "-" + parts[1] if len(parts) > 1 else f.replace(".md", "")
        ctitle = "-".join(parts[2:]) if len(parts) > 2 else f.replace(".md", "")
        try:
            with open(fpath, "r", encoding="utf-8") as fp: text = fp.read()
            full_text_db[cid] = {"id": cid, "title": f.replace(".md", ""), "text": text}
            d10_cards.append({"id": cid, "title": ctitle})
        except Exception:
            pass

    # 3. 解析 D20 目标
    d20_cards = []
    for fpath in l2_files:
        f = fpath.name
        parts = f.replace(".md", "").split("-")
        cid = parts[0] + "-" + parts[1] if len(parts) > 1 else f.replace(".md", "")
        ctitle = "-".join(parts[2:]) if len(parts) > 2 else f.replace(".md", "")
        try:
            with open(fpath, "r", encoding="utf-8") as fp: text = fp.read()
            full_text_db[cid] = {"id": cid, "title": f.replace(".md", ""), "text": text}
            ref_matches = re.findall(r"\[\[(D10-[^\]]+)\]\]", text)
            d1_refs = list(set([m.split("-")[0] + "-" + m.split("-")[1] for m in ref_matches if "-" in m]))
            if not d1_refs: d1_refs = ["D10-00"]
            d20_cards.append({"id": cid, "title": ctitle, "d1_refs": d1_refs})
        except Exception:
            pass

    # 4. 解析 D30 AOP 切面
    d30_to_d20_fallback = {
        "D30-01": ["D20-00"], "D30-02": ["D20-01"], "D30-03": ["D20-03"], "D30-04": ["D20-03"],
        "D30-05": ["D20-05"], "D30-06": ["D20-03"], "D30-07": ["D20-04"], "D30-08": ["D20-06"],
        "D30-09": ["D20-03"], "D30-10": ["D20-02"], "D30-11": ["D20-04"]
    }

    d30_cards = []
    for fpath in l3_files:
        f = fpath.name
        parts = f.replace(".md", "").split("-")
        cid = parts[0] + "-" + parts[1] if len(parts) > 1 else f.replace(".md", "")
        ctitle = "-".join(parts[2:]) if len(parts) > 2 else f.replace(".md", "")
        try:
            with open(fpath, "r", encoding="utf-8") as fp: text = fp.read()
            full_text_db[cid] = {"id": cid, "title": f.replace(".md", ""), "text": text}
            d2_matches1 = re.findall(r"\[\[(D20-[^\]]+)\]\]", text)
            d2_refs = list(set([m.split("-")[0] + "-" + m.split("-")[1] for m in d2_matches1 if "-" in m]))
            if not d2_refs and cid in d30_to_d20_fallback: d2_refs = d30_to_d20_fallback[cid]

            d30_cards.append({"id": cid, "title": ctitle, "d2_refs": d2_refs})
        except Exception:
            pass

    # 5. 解析 D40 需求 Tickets
    d40_cards = []
    for fpath in l4_files:
        f = fpath.name
        parts = f.replace(".md", "").split("-")
        cid = parts[0] + "-" + parts[1] if len(parts) > 1 else f.replace(".md", "")
        ctitle = "-".join(parts[2:]) if len(parts) > 2 else f.replace(".md", "")
        try:
            with open(fpath, "r", encoding="utf-8") as fp: text = fp.read()
            full_text_db[cid] = {"id": cid, "title": f.replace(".md", ""), "text": text}

            obsidian_svgs = re.findall(r"!\[\[([^\]]+\.svg)\]\]", text)
            md_svgs = re.findall(r"!\[[^\]]*\]\((?:file://)?(?:[^\)]*?/)?([^/\)]+\.svg)\)", text)
            svg_links = list(set(obsidian_svgs + md_svgs))
            svg_b64_urls = []
            for svg_item in svg_links:
                fname = os.path.basename(svg_item)
                if fname in svg_db:
                    svg_b64_urls.append(svg_db[fname])

            d3_matches1 = re.findall(r"\[\[(D30-[^\]]+)\]\]", text)
            d3_refs = list(set([m.split("-")[0] + "-" + m.split("-")[1] for m in d3_matches1 if "-" in m]))

            d40_cards.append({
                "id": cid,
                "title": ctitle,
                "d3_refs": d3_refs,
                "svg_b64_urls": svg_b64_urls
            })
        except Exception:
            pass

    # 6. 执行审计
    audit_data = {}
    if audit_engine:
        try:
            layer_nodes = {
                "layer1": audit_engine.collect_layer_nodes(layer1_dir or d10_dir, base_dir, "D1"),
                "layer2": audit_engine.collect_layer_nodes(layer2_dir or d20_dir, base_dir, "D2"),
                "layer3": audit_engine.collect_layer_nodes(layer3_dir or d30_dir, base_dir, "D3"),
                "layer4": audit_engine.collect_layer_nodes(layer4_dir or d40_dir, base_dir, "D4")
            }
            all_map = {}
            for l_key, l_files in layer_nodes.items():
                for pf in l_files:
                    n = audit_engine.process_file(pf)
                    if n: all_map[n["id"]] = n
            
            audit_data = audit_engine.perform_audit(all_map, {
                "layer1": [all_map[k] for k in all_map if k.startswith("D1")],
                "layer2": [all_map[k] for k in all_map if k.startswith("D2")],
                "layer3": [all_map[k] for k in all_map if k.startswith("D3")],
                "layer4": [all_map[k] for k in all_map if k.startswith("D4")]
            }, base_dir)
        except Exception as e:
            print(f"提示: 审计生成告警: {e}", file=sys.stderr)

    # 7. 生成源码
    commit_hash = get_git_commit_hash(base_dir)
    html_content = generate_full_buttons_dashboard_html(project_name, d10_cards, d20_cards, d30_cards, d40_cards, full_text_db, audit_data, svg_db, commit_hash)

    if output_html_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
        with open(output_html_path, "w", encoding="utf-8") as fp:
            fp.write(html_content)
        print(f"Successfully compiled Mesh Dashboard HTML -> {output_html_path}")

    return html_content

def safe_json_dump(data):
    """防止 </script> 导致脚本断裂的安全 JSON 字符串序列化"""
    s = json.dumps(data, ensure_ascii=False)
    return s.replace("</script>", "<\\/script>").replace("<!--", "<\\/--")

def generate_full_buttons_dashboard_html(project_name, d10_cards, d20_cards, d30_cards, d40_cards, full_text_db, audit_data, svg_db, commit_hash=""):
    """加回详情按钮并保留点击卡片保持高亮的 HTML 模版"""
    d10_json = safe_json_dump(d10_cards)
    d20_json = safe_json_dump(d20_cards)
    d30_json = safe_json_dump(d30_cards)
    d40_json = safe_json_dump(d40_cards)
    db_json = safe_json_dump(full_text_db)
    audit_json = safe_json_dump(audit_data)
    svg_db_json = safe_json_dump(svg_db)

    page_title = f"{project_name} ({commit_hash}) 项目整体设计预览" if commit_hash else f"{project_name} 项目整体设计预览"
    commit_badge = f'<span class="font-mono" style="font-size:11px; background:#e1e4e8; color:#0969da; padding:2px 6px; border-radius:3px; font-weight:500;">git: {commit_hash}</span>' if commit_hash else ''

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{page_title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    html, body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #f6f8fa;
      color: #1f2328;
      height: 100%;
      min-height: 100%;
      max-height: 100%;
      width: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }}

    .font-mono {{
      font-family: ui-monospace, SFMono-Regular, "Menlo", "Monaco", "Consolas", monospace;
    }}

    header {{
      height: 42px;
      min-height: 42px;
      background: #f6f8fa;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      position: relative;
      z-index: 30;
      border-bottom: 1px solid #d0d7de;
      flex-shrink: 0;
    }}
    .brand {{
      font-size: 13px;
      font-weight: 600;
      color: #1f2328;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .controls {{ display: flex; gap: 8px; align-items: center; }}
    
    .btn {{
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 500;
      border-radius: 2px;
      border: none;
      background: #1f2328;
      color: #ffffff;
      cursor: pointer;
      transition: background-color 0.12s ease;
    }}
    .btn:hover {{
      background: #0969da;
      color: #ffffff;
    }}
    .btn-audit {{
      background: #1f2328;
      color: #ffffff;
    }}
    .btn-audit:hover {{
      background: #0969da;
      color: #ffffff;
    }}
    .btn-pinned {{
      background: #cf222e;
      color: #ffffff;
    }}
    .btn-cancel-highlight {{
      background: #0969da;
      color: #ffffff;
    }}
    .btn-cancel-highlight:hover {{
      background: #0860c4;
    }}

    .view-wrapper {{
      flex: 1 1 0%;
      min-height: 0;
      height: 100%;
      position: relative;
      display: flex;
      overflow: hidden;
    }}

    #bezierCanvas {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 25;
    }}

    .finder-container {{
      flex: 1 1 0%;
      min-height: 0;
      height: 100%;
      display: flex;
      gap: 10px;
      padding: 10px 14px;
      overflow-x: auto;
      background: #f6f8fa;
      position: relative;
      z-index: 10;
    }}
    .finder-col {{
      flex: 1 1 0%;
      min-width: 290px;
      min-height: 0;
      height: 100%;
      background: #ffffff;
      border: 1px solid #d0d7de;
      border-radius: 3px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .col-header {{
      padding: 10px 14px;
      background: #f6f8fa;
      font-size: 12px;
      font-weight: 600;
      color: #57606a;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #d0d7de;
      flex-shrink: 0;
    }}
    .col-count {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      color: #8c959f;
    }}

    .col-body {{
      flex: 1 1 0%;
      min-height: 0;
      padding: 8px;
      overflow-y: auto;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
      gap: 0;
      -webkit-overflow-scrolling: touch;
    }}

    .card {{
      background: #ffffff;
      border: 1px solid #d0d7de;
      border-radius: 2px;
      padding: 10px 12px;
      cursor: pointer;
      transition: border-color 0.12s ease, box-shadow 0.12s ease;
      position: relative;
      margin-bottom: 8px;
    }}
    
    .card::after {{
      content: "";
      position: absolute;
      top: -4px;
      bottom: -4px;
      left: 0;
      right: 0;
      z-index: 1;
      pointer-events: auto;
    }}

    .card:hover {{
      border-color: #0969da;
    }}
    .card-id {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      font-weight: 600;
      color: #0969da;
      margin-bottom: 2px;
      position: relative;
      z-index: 2;
    }}
    .card-title {{
      font-size: 12px;
      font-weight: 600;
      color: #1f2328;
      line-height: 1.35;
      position: relative;
      z-index: 2;
    }}

    .card-actions {{
      display: flex;
      gap: 6px;
      margin-top: 8px;
      justify-content: flex-end;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.15s ease, visibility 0.15s ease;
      position: relative;
      z-index: 3;
    }}
    .card:hover .card-actions {{
      opacity: 1;
      visibility: visible;
    }}
    
    .mini-btn {{
      font-size: 11px;
      font-weight: 500;
      padding: 2px 7px;
      border-radius: 2px;
      background: #24292f;
      border: none;
      color: #ffffff;
      cursor: pointer;
      transition: background-color 0.12s ease;
    }}
    .mini-btn:hover {{
      background: #0969da;
      color: #ffffff;
    }}

    .card.hover-target {{
      border-color: #0969da !important;
      box-shadow: inset 0 0 0 1px #0969da, 0 2px 8px rgba(9, 105, 218, 0.12) !important;
      background: #ffffff !important;
      z-index: 10;
    }}
    .card.hover-neighbor {{
      border-color: #1f2328 !important;
      box-shadow: inset 0 0 0 1px #1f2328 !important;
      background: #ffffff !important;
      z-index: 5;
    }}
    .card.dimmed {{
      opacity: 0.25;
    }}

    .svg-preview-box {{
      margin-top: 8px;
      padding: 6px;
      background: #f6f8fa;
      border: 1px solid #e1e4e8;
      border-radius: 2px;
      max-height: 140px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      z-index: 2;
    }}
    .svg-preview-box img {{
      max-width: 100%;
      max-height: 120px;
      object-fit: contain;
    }}

    .modal-backdrop {{
      position: fixed;
      top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(31, 35, 40, 0.3);
      backdrop-filter: blur(2px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }}
    .modal-box {{
      width: 85%; max-width: 960px; max-height: 88vh;
      background: #ffffff;
      border: 1px solid #d0d7de;
      border-radius: 4px;
      display: flex; flex-direction: column; overflow: hidden;
      box-shadow: 0 16px 36px rgba(31, 35, 40, 0.2);
    }}
    .modal-header {{
      padding: 12px 20px;
      background: #f8f9fa;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #d0d7de;
    }}

    .markdown-body {{
      padding: 24px 28px;
      flex: 1;
      overflow-y: auto;
      font-size: 13px;
      line-height: 1.7;
      color: #1f2328;
      background: #ffffff;
    }}
    .markdown-body h1 {{
      font-size: 20px;
      font-weight: 700;
      color: #0969da;
      margin-bottom: 14px;
      border-bottom: 1px solid #d0d7de;
      padding-bottom: 6px;
    }}
    .markdown-body h2 {{
      font-size: 16px;
      font-weight: 600;
      color: #1f2328;
      margin-top: 20px;
      margin-bottom: 10px;
      border-bottom: 1px dashed #e1e4e8;
      padding-bottom: 4px;
    }}
    .markdown-body h3 {{
      font-size: 14px;
      font-weight: 600;
      color: #24292f;
      margin-top: 14px;
      margin-bottom: 8px;
    }}
    .markdown-body p {{
      margin-bottom: 12px;
      color: #333;
    }}
    .markdown-body ul {{
      margin: 8px 0 14px 20px;
      list-style-type: disc;
    }}
    .markdown-body li {{
      margin-bottom: 4px;
    }}
    .markdown-body hr {{
      border: none;
      border-top: 1px solid #d0d7de;
      margin: 18px 0;
    }}
    .markdown-body code {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      background: #f6f8fa;
      padding: 2px 6px;
      border-radius: 3px;
      border: 1px solid #e1e4e8;
      color: #0969da;
    }}
    .markdown-body pre {{
      background: #f6f8fa;
      padding: 12px;
      border-radius: 3px;
      border: 1px solid #d0d7de;
      overflow-x: auto;
      margin: 12px 0;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
    }}
    .markdown-body blockquote {{
      border-left: 3px solid #0969da;
      padding-left: 12px;
      color: #57606a;
      margin: 10px 0;
      background: #f8f9fa;
      padding-top: 6px;
      padding-bottom: 6px;
    }}
    
    .modal-svg-card {{
      margin: 16px 0;
      padding: 14px;
      background: #ffffff;
      border: 1px solid #d0d7de;
      border-radius: 4px;
      text-align: center;
      box-shadow: 0 2px 8px rgba(31,35,40,0.06);
    }}
    .modal-svg-card img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
    }}
    .modal-svg-title {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      color: #57606a;
      margin-top: 10px;
      font-weight: 500;
      border-top: 1px dashed #e1e4e8;
      padding-top: 6px;
    }}

    .frontmatter-footer-box {{
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px dashed #d0d7de;
    }}
    .frontmatter-footer-title {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 10px;
      font-weight: 600;
      color: #8c959f;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .frontmatter-footer-pre {{
      background: #f6f8fa;
      border: 1px solid #e1e4e8;
      border-radius: 3px;
      padding: 10px 12px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      line-height: 1.5;
      color: #6a737d;
      white-space: pre-wrap;
      word-break: break-all;
      margin: 0;
    }}

    .wikilink-tag {{
      color: #0969da;
      font-weight: 500;
      background: #f0f6fc;
      padding: 1px 5px;
      border-radius: 3px;
      cursor: pointer;
      text-decoration: none;
    }}
    .wikilink-tag:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

<header>
  <div class="brand">
    <span>{project_name} 项目整体设计预览</span>
    {commit_badge}
  </div>
  <div class="controls">
    <button class="btn" onclick="toggleInfoModal()">界面说明</button>
    <button class="btn btn-audit" onclick="toggleAuditModal()">遗漏审计报告</button>
    <button id="cancelHighlightBtn" class="btn btn-cancel-highlight" style="display:none;" onclick="cancelLockHighlight()">取消高亮</button>
    <button id="pinnedBtn" class="btn btn-pinned" style="display:none;" onclick="cancelPinned()">取消优先置顶并复原排序</button>
  </div>
</header>

<div class="view-wrapper" id="viewWrapper">
  <svg id="bezierCanvas"></svg>

  <div class="finder-container" id="finderContainer">
    <div class="finder-col">
      <div class="col-header"><span>D10 整体定位</span><span class="col-count" id="c1Count">0</span></div>
      <div class="col-body" id="col1"></div>
    </div>
    <div class="finder-col">
      <div class="col-header"><span>D20 可能的重点目标</span><span class="col-count" id="c2Count">0</span></div>
      <div class="col-body" id="col2"></div>
    </div>
    <div class="finder-col">
      <div class="col-header"><span>D30 产品功能切面</span><span class="col-count" id="c3Count">0</span></div>
      <div class="col-body" id="col3"></div>
    </div>
    <div class="finder-col">
      <div class="col-header"><span>D40 具体需求 Tickets</span><span class="col-count" id="c4Count">0</span></div>
      <div class="col-body" id="col4"></div>
    </div>
  </div>
</div>

<!-- Modal Document Viewer -->
<div class="modal-backdrop" id="docModal">
  <div class="modal-box">
    <div class="modal-header">
      <span id="modalTitle" class="font-mono" style="font-weight:600; color:#0969da;"></span>
      <button class="btn" onclick="closeModal('docModal')">关闭</button>
    </div>
    <div class="markdown-body" id="modalContent"></div>
  </div>
</div>

<!-- Modal Audit Viewer -->
<div class="modal-backdrop" id="auditModal">
  <div class="modal-box">
    <div class="modal-header">
      <span class="font-mono" style="font-weight:600; color:#1f2328;">完整性与未放进去内容审计报告</span>
      <button class="btn" onclick="closeModal('auditModal')">关闭</button>
    </div>
    <div class="markdown-body" id="auditContent"></div>
  </div>
</div>

<!-- Modal Info Viewer -->
<div class="modal-backdrop" id="infoModal">
  <div class="modal-box">
    <div class="modal-header">
      <span class="font-mono" style="font-weight:600; color:#0969da;">项目需求架构与界面使用说明</span>
      <button class="btn" onclick="closeModal('infoModal')">关闭</button>
    </div>
    <div class="markdown-body">
      <h1>一、项目需求拆解结构（AOP 4 层模型）</h1>
      <p>本界面将系统的完整设计与研发需求分为 4 列展示，从左到右依次为：</p>
      
      <ul>
        <li><b>D10 整体定位</b>：系统的核心定位、业务场景与要解决的问题。回答“为什么做”与“做给谁用”。</li>
        <li><b>D20 可能的重点目标</b>：定位对应的关键交付目标与衡量指标。回答“做成什么样”。</li>
        <li><b>D30 产品功能切面</b>：按功能模块（如能力引擎、持久化存储、UI 交互等）切分出的横向架构。每个切面关注独立的逻辑。</li>
        <li><b>D40 具体需求 Tickets</b>：可直接排期落地的原子 Ticket，包含具体交互逻辑、API 接口定义和界面架构示意图。</li>
      </ul>

      <hr>

      <h1>二、界面功能与检索方式</h1>
      <p>本 Dashboard 方便产品和开发快速检索与理解关联逻辑：</p>

      <ul>
        <li><b>全景浏览</b>：在同一页面上直接横向查看从“整体定位”到“具体 Ticket”的完整演进关系，无需层级目录跳转。</li>
        <li><b>关联查看与锁定高亮</b>：
          <ul>
            <li><b>鼠标悬停</b>或<b>点击任意卡片</b>：自动高亮该卡片，并绘制连线指向其<b>直接相关的上游目标</b>与<b>下游需求</b>；</li>
            <li><b>取消高亮</b>：点击顶栏右上角的「取消高亮」按钮，即可取消锁定，恢复随鼠标悬停随动。</li>
          </ul>
        </li>
        <li><b>查看全量文档与设计图</b>：点击卡片悬浮浮现的<b>「详情」</b>按钮，可打开全量 Markdown 文档与嵌入式 SVG UI Wireframe 图解。</li>
        <li><b>关联项优先置顶</b>：
          <ul>
            <li>点击任意卡片悬浮浮现的<b>“置顶”</b>按钮，该卡片及其上下游所有关联的任务和目标会<b>统一移动到各列最顶部</b>，方便集中对比分析；</li>
            <li>点击顶栏“取消优先置顶并复原排序”可恢复原始顺序。</li>
          </ul>
        </li>
        <li><b>数据遗漏与断链检查</b>：点击顶栏“遗漏审计报告”，可查看项目中是否有未挂载到体系中的游离文件或失效引用。</li>
      </ul>

      <hr>

      <h1>三、如何记录诉求</h1>
      <p>我们的需求记录与规划工作流包含以下 3 个步骤：</p>

      <ul>
        <li><b>1. 定义功能切面</b>：首先按系统模块或逻辑维度（如持久化存储、UI 交互、引擎能力等）定义切面，明确系统包含哪些要处理的事情。</li>
        <li><b>2. 自由收集与归拢需求</b>：团队成员可以用任意语言、Idea 或原始描述记录日常诉求，并将其分类归拢到对应的功能切面下。</li>
        <li><b>3. 评估价值与优先落地</b>：在各个切面内部梳理与评估需求优先级，选出价值最高、最关键的需求 Ticket 优先安排排期与开发。</li>
      </ul>
    </div>
  </div>
</div>

<script>
const rawD10 = {d10_json};
const rawD20 = {d20_json};
const rawD30 = {d30_json};
const rawD40 = {d40_json};

let D10 = [...rawD10];
let D20 = [...rawD20];
let D30 = [...rawD30];
let D40 = [...rawD40];

const DB = {db_json};
const AUDIT = {audit_json};
const SVG_DB = {svg_db_json};

let isPinnedMode = false;
let isLockedHighlightMode = false;
let activeHoverState = null;
let hoverLeaveTimer = null;

function init() {{
  renderCol1(); renderCol2(); renderCol3(); renderCol4();
  renderAuditReport();
  bindScrollEvents();
}}

/* 卡片包含「置顶」与「详情」两个完整按钮 */
function renderCol1() {{
  const col = document.getElementById("col1");
  document.getElementById("c1Count").innerText = D10.length;
  col.innerHTML = D10.map(item => `
    <div class="card" id="card-${{item.id}}" onclick="lockHighlight(event, '${{item.id}}', 'd10')" onmouseenter="onHover('${{item.id}}', 'd10')" onmouseleave="onLeave()">
      <div class="card-id">${{item.id}}</div>
      <div class="card-title">${{item.title}}</div>
      <div class="card-actions">
        <button class="mini-btn" onclick="pinItem(event, '${{item.id}}')">置顶</button>
        <button class="mini-btn" onclick="showDoc(event, '${{item.id}}')">详情</button>
      </div>
    </div>
  `).join('');
}}

function renderCol2() {{
  const col = document.getElementById("col2");
  document.getElementById("c2Count").innerText = D20.length;
  col.innerHTML = D20.map(item => `
    <div class="card" id="card-${{item.id}}" onclick="lockHighlight(event, '${{item.id}}', 'd20')" onmouseenter="onHover('${{item.id}}', 'd20')" onmouseleave="onLeave()">
      <div class="card-id">${{item.id}}</div>
      <div class="card-title">${{item.title}}</div>
      <div class="card-actions">
        <button class="mini-btn" onclick="pinItem(event, '${{item.id}}')">置顶</button>
        <button class="mini-btn" onclick="showDoc(event, '${{item.id}}')">详情</button>
      </div>
    </div>
  `).join('');
}}

function renderCol3() {{
  const col = document.getElementById("col3");
  document.getElementById("c3Count").innerText = D30.length;
  col.innerHTML = D30.map(item => `
    <div class="card" id="card-${{item.id}}" onclick="lockHighlight(event, '${{item.id}}', 'd30')" onmouseenter="onHover('${{item.id}}', 'd30')" onmouseleave="onLeave()">
      <div class="card-id">${{item.id}}</div>
      <div class="card-title">${{item.title}}</div>
      <div class="card-actions">
        <button class="mini-btn" onclick="pinItem(event, '${{item.id}}')">置顶</button>
        <button class="mini-btn" onclick="showDoc(event, '${{item.id}}')">详情</button>
      </div>
    </div>
  `).join('');
}}

function renderCol4() {{
  const col = document.getElementById("col4");
  document.getElementById("c4Count").innerText = D40.length;
  col.innerHTML = D40.map(item => `
    <div class="card" id="card-${{item.id}}" onclick="lockHighlight(event, '${{item.id}}', 'd40')" onmouseenter="onHover('${{item.id}}', 'd40')" onmouseleave="onLeave()">
      <div class="card-id">${{item.id}}</div>
      <div class="card-title">${{item.title}}</div>
      ${{item.svg_b64_urls && item.svg_b64_urls.length > 0 ? `<div class="svg-preview-box"><img src="${{item.svg_b64_urls[0]}}" alt="SVG Wireframe"></div>` : ''}}
      <div class="card-actions">
        <button class="mini-btn" onclick="pinItem(event, '${{item.id}}')">置顶</button>
        <button class="mini-btn" onclick="showDoc(event, '${{item.id}}')">详情</button>
      </div>
    </div>
  `).join('');
}}

function bindScrollEvents() {{
  document.querySelectorAll('.col-body').forEach(col => {{
    col.addEventListener('scroll', () => {{
      if (activeHoverState) {{
        drawAllBezierLinks(activeHoverState.id, activeHoverState.neighborIds);
      }}
    }});
  }});
}}

function lockHighlight(ev, id, type) {{
  if (ev) ev.stopPropagation();

  if (hoverLeaveTimer) {{
    clearTimeout(hoverLeaveTimer);
    hoverLeaveTimer = null;
  }}

  let neighborIds = getNeighborIds(id, type);

  isLockedHighlightMode = true;
  document.getElementById("cancelHighlightBtn").style.display = "inline-block";

  applyHighlightAndLinks(id, neighborIds);
}}

function cancelLockHighlight() {{
  isLockedHighlightMode = false;
  document.getElementById("cancelHighlightBtn").style.display = "none";
  
  if (!isPinnedMode) {{
    activeHoverState = null;
    onLeaveImmediate();
  }}
}}

function getNeighborIds(id, type) {{
  let neighborIds = [];
  if (type === 'd10') {{
    D20.filter(x => (x.d1_refs || []).includes(id)).forEach(x => neighborIds.push(x.id));
  }} else if (type === 'd20') {{
    const d2Item = D20.find(x => x.id === id);
    if (d2Item) (d2Item.d1_refs || []).forEach(r => neighborIds.push(r));
    D30.filter(x => (x.d2_refs || []).includes(id)).forEach(x => neighborIds.push(x.id));
  }} else if (type === 'd30') {{
    const d3Item = D30.find(x => x.id === id);
    if (d3Item) (d3Item.d2_refs || []).forEach(r => neighborIds.push(r));
    D40.filter(x => (x.d3_refs || []).includes(id)).forEach(x => neighborIds.push(x.id));
  }} else if (type === 'd40') {{
    const d4Item = D40.find(x => x.id === id);
    if (d4Item) (d4Item.d3_refs || []).forEach(r => neighborIds.push(r));
  }}
  return neighborIds;
}}

function onHover(id, type) {{
  if (hoverLeaveTimer) {{
    clearTimeout(hoverLeaveTimer);
    hoverLeaveTimer = null;
  }}

  if (isLockedHighlightMode || isPinnedMode) return;

  let neighborIds = getNeighborIds(id, type);
  applyHighlightAndLinks(id, neighborIds);
}}

function applyHighlightAndLinks(targetId, neighborIds) {{
  document.querySelectorAll('.card').forEach(c => {{
    c.classList.remove('hover-target', 'hover-neighbor');
    c.classList.add('dimmed');
  }});
  
  const target = document.getElementById('card-' + targetId);
  if (target) {{
    target.classList.remove('dimmed');
    target.classList.add('hover-target');
  }}

  neighborIds.forEach(nid => highlightNeighbor(nid));
  
  activeHoverState = {{ id: targetId, neighborIds }};
  drawAllBezierLinks(targetId, neighborIds);
}}

function highlightNeighbor(id) {{
  const el = document.getElementById('card-' + id);
  if (el) {{
    el.classList.remove('dimmed');
    el.classList.add('hover-neighbor');
  }}
}}

function onLeave() {{
  if (isLockedHighlightMode || isPinnedMode) return;
  
  if (hoverLeaveTimer) clearTimeout(hoverLeaveTimer);
  
  hoverLeaveTimer = setTimeout(() => {{
    onLeaveImmediate();
  }}, 120);
}}

function onLeaveImmediate() {{
  document.querySelectorAll('.card').forEach(c => {{
    c.classList.remove('dimmed', 'hover-target', 'hover-neighbor');
  }});
  clearBezierCanvas();
  activeHoverState = null;
  hoverLeaveTimer = null;
}}

function drawAllBezierLinks(targetId, neighborIds) {{
  clearBezierCanvas();
  const canvas = document.getElementById("bezierCanvas");
  const wrapperRect = document.getElementById("viewWrapper").getBoundingClientRect();
  const targetEl = document.getElementById('card-' + targetId);
  if (!targetEl || !canvas) return;

  const tRect = targetEl.getBoundingClientRect();
  const tX_center = tRect.left + tRect.width / 2 - wrapperRect.left;
  const tY = tRect.top + tRect.height / 2 - wrapperRect.top;

  let svgElements = '';

  neighborIds.forEach(nid => {{
    const nEl = document.getElementById('card-' + nid);
    if (!nEl) return;
    const nRect = nEl.getBoundingClientRect();
    const nX_center = nRect.left + nRect.width / 2 - wrapperRect.left;
    const nY = nRect.top + nRect.height / 2 - wrapperRect.top;

    let p1X, p1Y, p2X, p2Y;

    if (tX_center < nX_center) {{
      p1X = tRect.right - wrapperRect.left;
      p1Y = tY;
      p2X = nRect.left - wrapperRect.left;
      p2Y = nY;
    }} else {{
      p1X = tRect.left - wrapperRect.left;
      p1Y = tY;
      p2X = nRect.right - wrapperRect.left;
      p2Y = nY;
    }}

    const dx = Math.abs(p2X - p1X) * 0.45;
    const cp1X = p1X < p2X ? p1X + dx : p1X - dx;
    const cp2X = p1X < p2X ? p2X - dx : p2X + dx;
    const pathData = `M ${{p1X}} ${{p1Y}} C ${{cp1X}} ${{p1Y}}, ${{cp2X}} ${{p2Y}}, ${{p2X}} ${{p2Y}}`;

    svgElements += `
      <path d="${{pathData}}" stroke="#0969da" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.85" />
      <circle cx="${{p1X}}" cy="${{p1Y}}" r="3.5" fill="#0969da" />
      <circle cx="${{p2X}}" cy="${{p2Y}}" r="3.5" fill="#0969da" />
    `;
  }});

  canvas.innerHTML = svgElements;
}}

function clearBezierCanvas() {{
  const canvas = document.getElementById("bezierCanvas");
  if (canvas) canvas.innerHTML = '';
}}

function pinItem(ev, id) {{
  if (ev) ev.stopPropagation();
  
  let type = "d10";
  if (id.startsWith("D20")) type = "d20";
  else if (id.startsWith("D30")) type = "d30";
  else if (id.startsWith("D40")) type = "d40";

  let neighborIds = getNeighborIds(id, type);
  const pinnedSet = new Set([id, ...neighborIds]);

  D10 = [...D10.filter(x => pinnedSet.has(x.id)), ...D10.filter(x => !pinnedSet.has(x.id))];
  D20 = [...D20.filter(x => pinnedSet.has(x.id)), ...D20.filter(x => !pinnedSet.has(x.id))];
  D30 = [...D30.filter(x => pinnedSet.has(x.id)), ...D30.filter(x => !pinnedSet.has(x.id))];
  D40 = [...D40.filter(x => pinnedSet.has(x.id)), ...D40.filter(x => !pinnedSet.has(x.id))];

  renderCol1(); renderCol2(); renderCol3(); renderCol4();

  document.querySelectorAll('.col-body').forEach(col => col.scrollTop = 0);

  isPinnedMode = true;
  document.getElementById("pinnedBtn").style.display = "inline-block";

  setTimeout(() => {{
    applyHighlightAndLinks(id, neighborIds);
  }}, 30);
}}

function cancelPinned() {{
  isPinnedMode = false;
  document.getElementById("pinnedBtn").style.display = "none";

  D10 = [...rawD10];
  D20 = [...rawD20];
  D30 = [...rawD30];
  D40 = [...rawD40];

  renderCol1(); renderCol2(); renderCol3(); renderCol4();
  activeHoverState = null;
  onLeaveImmediate();
}}

function renderMarkdownText(text) {{
  if (!text) return "";

  let frontmatterRaw = null;
  const fmMatch = text.match(/^(?:---|\+\+\+)[\s\S]*?(?:---|\+\+\+)/);
  if (fmMatch) {{
    frontmatterRaw = fmMatch[0];
    text = text.substring(frontmatterRaw.length).trim();
  }}

  text = text.replace(/!\[\[([^\]]+\.svg)\]\]/g, (match, svgFilename) => {{
    let fname = svgFilename.split('/').pop();
    try {{ fname = decodeURIComponent(fname); }} catch(e) {{}}
    if (SVG_DB[fname]) {{
      return `<div class="modal-svg-card"><img src="${{SVG_DB[fname]}}" alt="${{fname}}"><div class="modal-svg-title">架构图解: ${{fname}}</div></div>`;
    }}
    return `<div class="modal-svg-card">[SVG 图片: ${{fname}}]</div>`;
  }});

  text = text.replace(/!\[([^\]]*)\]\((?:file:\/\/)?(?:[^\)]+?\/)?([^\/\)]+\.svg)\)/g, (match, alt, svgFilename) => {{
    let fname = svgFilename.split('/').pop();
    try {{ fname = decodeURIComponent(fname); }} catch(e) {{}}
    if (SVG_DB[fname]) {{
      return `<div class="modal-svg-card"><img src="${{SVG_DB[fname]}}" alt="${{alt || fname}}"><div class="modal-svg-title">架构图解: ${{alt || fname}}</div></div>`;
    }}
    return `<div class="modal-svg-card">[SVG 图片: ${{fname}}]</div>`;
  }});

  text = text.replace(/\[\[(D[1-5]0-[^\]]+)\]\]/g, (match, linkTarget) => {{
    const targetId = linkTarget.split("-")[0] + "-" + linkTarget.split("-")[1];
    return `<a class="wikilink-tag" onclick="showDocById('${{targetId}}')">${{linkTarget}}</a>`;
  }});

  const lines = text.split(/\\r?\\n/);
  let htmlResult = [];
  let inList = false;

  lines.forEach(line => {{
    let trimmed = line.trim();

    if (!trimmed.startsWith("* ") && !trimmed.startsWith("- ") && !trimmed.startsWith("+ ")) {{
      if (inList) {{
        htmlResult.push("</ul>");
        inList = false;
      }}
    }}

    if (trimmed.startsWith("# ")) {{
      htmlResult.push(`<h1>${{escapeHtml(trimmed.substring(2))}}</h1>`);
    }} else if (trimmed.startsWith("## ")) {{
      htmlResult.push(`<h2>${{escapeHtml(trimmed.substring(3))}}</h2>`);
    }} else if (trimmed.startsWith("### ")) {{
      htmlResult.push(`<h3>${{escapeHtml(trimmed.substring(4))}}</h3>`);
    }} else if (trimmed === "---" || trimmed === "***" || trimmed === "___") {{
      htmlResult.push("<hr>");
    }} else if (trimmed.startsWith("> ")) {{
      htmlResult.push(`blockquote>${{formatInlineMarkdown(trimmed.substring(2))}}</blockquote>`);
    }} else if (trimmed.startsWith("* ") || trimmed.startsWith("- ") || trimmed.startsWith("+ ")) {{
      if (!inList) {{
        htmlResult.push("<ul>");
        inList = true;
      }}
      htmlResult.push(`<li>${{formatInlineMarkdown(trimmed.substring(2))}}</li>`);
    }} else if (trimmed.startsWith('<div class="modal-svg-card"')) {{
      htmlResult.push(line);
    }} else if (trimmed === "") {{
      htmlResult.push("<br>");
    }} else {{
      htmlResult.push(`<p>${{formatInlineMarkdown(line)}}</p>`);
    }}
  }});

  if (inList) htmlResult.push("</ul>");

  if (frontmatterRaw) {{
    htmlResult.push(`
      <div class="frontmatter-footer-box">
        <div class="frontmatter-footer-title">Document Metadata (Frontmatter)</div>
        <pre class="frontmatter-footer-pre">${{escapeHtml(frontmatterRaw)}}</pre>
      </div>
    `);
  }}

  return htmlResult.join("\\n");
}}

function formatInlineMarkdown(str) {{
  if (!str) return "";
  str = str.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
  str = str.replace(/`([^`]+)`/g, '<code>$1</code>');
  return str;
}}

function escapeHtml(str) {{
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}}

function showDocById(targetId) {{
  const data = DB[targetId];
  if (data) {{
    document.getElementById("modalTitle").innerText = data.title;
    document.getElementById("modalContent").innerHTML = renderMarkdownText(data.text);
    document.getElementById("docModal").style.display = "flex";
  }}
}}

function showDoc(ev, id) {{
  if (ev) ev.stopPropagation();
  showDocById(id);
}}

function toggleInfoModal() {{
  document.getElementById("infoModal").style.display = "flex";
}}

function toggleAuditModal() {{
  document.getElementById("auditModal").style.display = "flex";
}}

function closeModal(id) {{
  document.getElementById(id).style.display = "none";
}}

function renderAuditReport() {{
  if (!AUDIT || !AUDIT.completeness_audit) return;
  const s = AUDIT.completeness_audit.summary;
  const f = AUDIT.completeness_audit.audit_findings;

  let html = `
    <h3 style="color:#0969da; margin-bottom:8px; font-weight:600;">4 层需求架构总体覆盖率: ${{s.aspect_coverage_rate_percent}}%</h3>
    <p style="color:#57606a;">全量节点: <b>${{s.total_nodes}}</b> | D10-xx 整体定位: ${{s.layer1_narrative_count}} | D20-xx 可能的重点目标: ${{s.layer2_targets_count}} | D30-xx 产品功能切面: ${{s.layer3_aspects_count}} | D40-xx 具体需求 Tickets: ${{s.layer4_tickets_count}}</p>
    <br>

    <h4 style="color:#cf222e;">双向引用断链与死链审计 (${{f.broken_links_count}} 处)</h4>
    ${{f.broken_links_count > 0 ? f.broken_links_list.map(b => `<div style="color:#cf222e; margin-top:4px;">❌ 源节点 <b>${{b.source_node}}</b> 引用了不存在的目标: <code>${{b.broken_target}}</code></div>`).join('') : '<div style="color:#1a7f37;">无断链</div>'}}

    <h4 style="color:#bf8700; margin-top:16px;">未被放进去/游离未分类文件审计 (${{f.unclassified_stray_files_count}} 个文件)</h4>
    <p style="color:#57606a; font-size:11px;">以下文件存在于项目目录中，但尚未被加上 4 层编号或未被引入体系：</p>
    <div style="background:#f8f9fa; border:1px solid #d0d7de; padding:8px 12px; border-radius:2px; max-height:220px; overflow-y:auto; margin-top:6px;">
      ${{f.unclassified_stray_files_list.map(path => `<div style="color:#1f2328; margin-bottom:2px;">📄 ${{path}}</div>`).join('')}}
    </div>

    <h4 style="color:#0969da; margin-top:16px;">未评估 6 维复杂度的 Ticket 列表 (${{f.unassessed_tickets_count}} 个)</h4>
    <div style="color:#1f2328;">${{f.unassessed_tickets_list.join(', ')}}</div>
  `;
  document.getElementById("auditContent").innerHTML = html;
}}

window.onload = init;
</script>
</body>
</html>
"""

def main():
    parser = argparse.ArgumentParser(description="AOP 需求架构 Finder 面板 Full Buttons Edition 编译脚本")
    parser.add_argument("--root-dir", "-r", default=".", help="项目根目录路径")
    parser.add_argument("--layer1-dir", "--d10-dir", help="第一层 (D10 整体定位) 定位目录或文件路径")
    parser.add_argument("--layer2-dir", "--d20-dir", help="第二层 (D20 可能的重点目标) 定位目录或文件路径")
    parser.add_argument("--layer3-dir", "--d30-dir", help="第三层 (D30 产品功能切面) 定位目录或文件路径")
    parser.add_argument("--layer4-dir", "--d40-dir", help="第四层 (D40 具体需求 Tickets) 定位目录或文件路径")
    parser.add_argument("--output", "-o", default="preview/index.html", help="输出网页 HTML 相对或绝对路径")

    args = parser.parse_args()

    compile_dashboard(
        root_dir=args.root_dir,
        layer1_dir=args.layer1_dir,
        layer2_dir=args.layer2_dir,
        layer3_dir=args.layer3_dir,
        layer4_dir=args.layer4_dir,
        output_html_path=args.output
    )

if __name__ == '__main__':
    main()
