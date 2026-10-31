#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOP 需求架构四层数据提取、审阅与完整性审计脚本 (Extract & Audit Mesh CLI)

该脚本解析项目中的 4 层 Markdown 策划与需求架构文档：
  - Layer 1 (D10): 故事与定位叙事
  - Layer 2 (D20): 平台目标与重点
  - Layer 3 (D30): AOP 切面大网
  - Layer 4 (D40): 需求 Tickets

提取所有元数据、双向引用与依赖拓扑，进行遗漏与完整性审计，
并导出格式化的 YAML 或 TOML 结构文件供团队审阅和分析。
"""

import os
import sys
import re
import argparse
from pathlib import Path
import json

def parse_frontmatter(content):
    """解析 Markdown 中的 YAML frontmatter (---) 或 TOML frontmatter (+++)"""
    fm = {}
    body = content
    
    # 尝试 YAML frontmatter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if yaml_match:
        raw_fm, body = yaml_match.group(1), yaml_match.group(2)
        fm = parse_simple_yaml(raw_fm)
        return fm, body

    # 尝试 TOML frontmatter
    toml_match = re.match(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)$', content, re.DOTALL)
    if toml_match:
        raw_fm, body = toml_match.group(1), toml_match.group(2)
        fm = parse_simple_yaml(raw_fm) # 轻量兼容
        return fm, body

    return fm, body

def parse_simple_yaml(raw_str):
    """简易 YAML 解析器（无需依赖第三方库）"""
    data = {}
    current_key = None
    current_list = None

    for line in raw_str.splitlines():
        line_strip = line.strip()
        if not line_strip or line_strip.startswith('#'):
            continue
        
        # 列表项
        if line_strip.startswith('- '):
            val = line_strip[2:].strip().strip('"\'')
            if current_key and current_list is not None:
                current_list.append(val)
            continue
            
        if ':' in line_strip:
            key, val = line_strip.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            
            if val == '':
                current_key = key
                current_list = []
                data[key] = current_list
            else:
                data[key] = val
                current_key = key
                current_list = None

    return data

def extract_wikilinks(text):
    """提取文本中的所有 Obsidian 双向引用 [[Link]]"""
    pattern = r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, text)
    return sorted(list(set(matches)))

def find_files_by_prefix(search_dir, prefix):
    """在指定目录中递归查找特定前缀的 .md 文件"""
    found = []
    if not search_dir or not os.path.exists(search_dir):
        return found
    
    path_obj = Path(search_dir)
    if path_obj.is_file():
        if path_obj.name.startswith(prefix) and path_obj.name.endswith('.md'):
            return [path_obj]
        return found

    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if f.startswith(prefix) and f.endswith('.md'):
                found.append(Path(root) / f)
    return sorted(found)

def collect_layer_nodes(target_dir, root_dir, prefix):
    """收集某一层的全部节点文件"""
    search_path = target_dir if target_dir else root_dir
    return find_files_by_prefix(search_path, prefix)

def process_file(file_path):
    """读取并提取单个 Markdown 文件的结构化节点数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"警告: 无法读取文件 {file_path}: {e}", file_stderr=True)
        return None

    fm, body = parse_frontmatter(content)
    wikilinks = extract_wikilinks(content)
    stem = file_path.stem

    node = {
        "id": stem,
        "filename": file_path.name,
        "path": str(file_path),
        "title": fm.get("title", stem),
        "date_created": fm.get("date created") or fm.get("date_created", "未记录"),
        "creator": fm.get("creator", "未记录"),
        "background": fm.get("background", ""),
        "references": fm.get("references", []),
        "depends_on_tickets": fm.get("depends_on_tickets", []),
        "related_aspects": fm.get("related_aspects", []),
        "initial_complexity_assessment": fm.get("initial_complexity_assessment", {}),
        "outgoing_links": wikilinks
    }
    return node

def dump_yaml(data_dict, indent=0):
    """纯 Python 自制 YAML 格式化输出函数（保证无第三方依赖环境兼容）"""
    lines = []
    ind_str = "  " * indent
    
    if isinstance(data_dict, dict):
        for k, v in data_dict.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{ind_str}{k}:")
                lines.append(dump_yaml(v, indent + 1))
            else:
                str_v = str(v) if v is not None else ""
                if "\n" in str_v or '"' in str_v or "'" in str_v or ":" in str_v:
                    str_v = f'"{str_v}"'
                lines.append(f"{ind_str}{k}: {str_v}")
    elif isinstance(data_dict, list):
        for item in data_dict:
            if isinstance(item, (dict, list)):
                lines.append(f"{ind_str}-")
                lines.append(dump_yaml(item, indent + 1))
            else:
                str_item = str(item) if item is not None else ""
                lines.append(f"{ind_str}- \"{str_item}\"")
    return "\n".join(lines)

def dump_toml(data_dict, prefix=""):
    """纯 Python 简易 TOML 格式化输出函数"""
    lines = []
    tables = []
    
    for k, v in data_dict.items():
        if isinstance(v, dict):
            new_prefix = f"{prefix}.{k}" if prefix else k
            tables.append((new_prefix, v))
        elif isinstance(v, list):
            # 列表支持
            if not v:
                lines.append(f'{k} = []')
            elif isinstance(v[0], dict):
                for item in v:
                    new_prefix = f"{prefix}.{k}" if prefix else k
                    tables.append((new_prefix, item))
            else:
                formatted_items = [f'"{x}"' for x in v]
                lines.append(f'{k} = [{", ".join(formatted_items)}]')
        else:
            str_v = str(v) if v is not None else ""
            lines.append(f'{k} = "{str_v}"')
            
    res = "\n".join(lines)
    for tab_name, tab_dict in tables:
        res += f"\n\n[{tab_name}]\n"
        res += dump_toml(tab_dict, tab_name)
    return res

def perform_audit(all_nodes_map, layer_nodes, root_dir):
    """四层完整性与遗漏审计引擎（含未纳入四层的游离/遗漏文件审计）"""
    all_existing_ids = set(all_nodes_map.keys())
    
    d10_nodes = layer_nodes.get("layer1", [])
    d20_nodes = layer_nodes.get("layer2", [])
    d30_nodes = layer_nodes.get("layer3", [])
    d40_nodes = layer_nodes.get("layer4", [])

    d30_ids = set(n["id"] for n in d30_nodes)
    d40_ids = set(n["id"] for n in d40_nodes)

    # 1. 查找被关联的 D30 切面集合（在 D40 的 related_aspects 或 references 中）
    referenced_d30 = set()
    for d40 in d40_nodes:
        aspects = d40.get("related_aspects", [])
        if isinstance(aspects, list):
            for a in aspects:
                clean_a = a.replace("[[", "").replace("]]", "").strip()
                if clean_a in d30_ids:
                    referenced_d30.add(clean_a)
        # 从 outgoing_links 补充
        for link in d40.get("outgoing_links", []):
            if link in d30_ids:
                referenced_d30.add(link)

    # 裸切面 (没有任何 D40 填补实现的空 D30)
    naked_aspects = sorted(list(d30_ids - referenced_d30))

    # 2. 孤立 Ticket (未关联任何 D30 AOP 切面的 D40)
    unmapped_tickets = []
    for d40 in d40_nodes:
        has_aspect = False
        aspects = d40.get("related_aspects", [])
        if isinstance(aspects, list):
            for a in aspects:
                clean_a = a.replace("[[", "").replace("]]", "").strip()
                if clean_a.startswith("D30-"):
                    has_aspect = True
                    break
        if not has_aspect:
            for link in d40.get("outgoing_links", []):
                if link.startswith("D30-"):
                    has_aspect = True
                    break
        if not has_aspect:
            unmapped_tickets.append(d40["id"])

    # 3. 死链检测 (Broken Links)
    broken_links = []
    for node in all_nodes_map.values():
        for link in node.get("outgoing_links", []):
            if (link.startswith("D10-") or link.startswith("D20-") or link.startswith("D30-") or link.startswith("D40-")) and link not in all_existing_ids:
                broken_links.append({
                    "source_node": node["id"],
                    "broken_target": link
                })

    # 4. 未评估复杂度/工时统计 (Unassessed Tickets)
    unassessed_tickets = []
    for d40 in d40_nodes:
        c = d40.get("initial_complexity_assessment", {})
        if isinstance(c, dict):
            values = list(c.values())
            if not values or any(v == "未评估" for v in values):
                unassessed_tickets.append(d40["id"])

    # 5. 未被放进去的未分类/游离文件审计 (Unclassified / Omitted Stray Files)
    unclassified_stray_files = []
    if root_dir and os.path.exists(root_dir):
        ignore_names = {"AGENTS.md", "HANDOFF.md", "README.md", "DESIGN.md", "SKILL.md"}
        all_referenced_titles = set(all_nodes_map.keys())
        for node in all_nodes_map.values():
            for ref in node.get("references", []):
                clean_ref = ref.replace("[[", "").replace("]]", "").replace('"', '').strip()
                all_referenced_titles.add(clean_ref)

        for r, d, files in os.walk(root_dir):
            # 过滤 _attachments, .git, preview 等目录
            if any(p in r for p in ["_attachments", ".git", "preview", "node_modules"]):
                continue
            for f in files:
                if f.endswith('.md') and f not in ignore_names:
                    stem = Path(f).stem
                    if stem not in all_existing_ids and not any(stem.startswith(p) for p in ["D1", "D2", "D3", "D4"]):
                        rel_path = os.path.relpath(os.path.join(r, f), root_dir)
                        unclassified_stray_files.append(rel_path)

    total_count = len(all_nodes_map)
    coverage_score = ((len(d30_ids) - len(naked_aspects)) / len(d30_ids) * 100) if d30_ids else 100.0

    return {
        "summary": {
            "total_nodes": total_count,
            "layer1_narrative_count": len(d10_nodes),
            "layer2_targets_count": len(d20_nodes),
            "layer3_aspects_count": len(d30_nodes),
            "layer4_tickets_count": len(d40_nodes),
            "aspect_coverage_rate_percent": round(coverage_score, 2)
        },
        "audit_findings": {
            "naked_aspects_count": len(naked_aspects),
            "naked_aspects_list": naked_aspects,
            "unmapped_tickets_count": len(unmapped_tickets),
            "unmapped_tickets_list": unmapped_tickets,
            "broken_links_count": len(broken_links),
            "broken_links_list": broken_links,
            "unassessed_tickets_count": len(unassessed_tickets),
            "unassessed_tickets_list": unassessed_tickets,
            "unclassified_stray_files_count": len(unclassified_stray_files),
            "unclassified_stray_files_list": sorted(unclassified_stray_files)
        }
    }

def main():
    parser = argparse.ArgumentParser(description="AOP 需求架构四层数据提取、审阅与完整性审计工具")
    parser.add_argument("--root-dir", "-r", default=".", help="项目根目录路径")
    parser.add_argument("--layer1-dir", "--d10-dir", help="第一层 (D10 叙事) 定位目录/文件")
    parser.add_argument("--layer2-dir", "--d20-dir", help="第二层 (D20 目标) 定位目录/文件")
    parser.add_argument("--layer3-dir", "--d30-dir", help="第三层 (D30 切面) 定位目录/文件")
    parser.add_argument("--layer4-dir", "--d40-dir", help="第四层 (D40 Tickets) 定位目录/文件")
    parser.add_argument("--format", "-f", choices=["yaml", "toml", "json"], default="yaml", help="输出结构化格式 (yaml/toml/json)")
    parser.add_argument("--output", "-o", help="输出目标文件路径 (如 audit_result.yaml)")
    parser.add_argument("--check-completeness", action="store_true", default=True, help="是否包含完整性审计报告")

    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    print(f"正在扫描与提取四层需求架构... 根目录: {root_dir}")

    # 查找四层文件 (D1x 属于第一层, D2x 属于第二层, D3x 属于第三层, D4x 属于第四层)
    files_l1 = collect_layer_nodes(args.layer1_dir, root_dir, "D1")
    files_l2 = collect_layer_nodes(args.layer2_dir, root_dir, "D2")
    files_l3 = collect_layer_nodes(args.layer3_dir, root_dir, "D3")
    files_l4 = collect_layer_nodes(args.layer4_dir, root_dir, "D4")

    nodes_l1 = [process_file(f) for f in files_l1 if process_file(f)]
    nodes_l2 = [process_file(f) for f in files_l2 if process_file(f)]
    nodes_l3 = [process_file(f) for f in files_l3 if process_file(f)]
    nodes_l4 = [process_file(f) for f in files_l4 if process_file(f)]

    all_nodes_map = {}
    for node_list in [nodes_l1, nodes_l2, nodes_l3, nodes_l4]:
        for n in node_list:
            all_nodes_map[n["id"]] = n

    layer_nodes_map = {
        "layer1": nodes_l1,
        "layer2": nodes_l2,
        "layer3": nodes_l3,
        "layer4": nodes_l4
    }

    # 执行审计
    audit_report = perform_audit(all_nodes_map, layer_nodes_map, root_dir)

    final_result = {
        "project_mesh_audit": {
            "root_directory": root_dir,
            "layer1_narratives": nodes_l1,
            "layer2_targets": nodes_l2,
            "layer3_aspects": nodes_l3,
            "layer4_tickets": nodes_l4,
            "completeness_audit": audit_report
        }
    }

    # 导出序列化文本
    out_format = args.format.lower()
    if out_format == "json":
        output_str = json.dumps(final_result, ensure_ascii=False, indent=2)
    elif out_format == "toml":
        output_str = dump_toml(final_result)
    else:
        output_str = dump_yaml(final_result)

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"成功导出四层架构审阅与审计数据 -> {out_path}")
    else:
        print("\n==================== 审计与提取结果 ====================")
        print(output_str)

if __name__ == '__main__':
    main()
