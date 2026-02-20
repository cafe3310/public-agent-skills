import os
import argparse
import yaml
import re
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Add the workflows/01_ingest directory to sys.path to import SCRIPT_util
sys.path.append(str(Path(__file__).parent.parent / "01_ingest"))
from SCRIPT_util import RegexPatterns

# --- YAML Multi-line Support ---
class LiteralStr(str):
    """Custom string type to force PyYAML to use the | literal block style."""
    pass

def literal_presenter(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(LiteralStr, literal_presenter)
# ------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze data gaps with refined 'sandwich' context logic.")
    parser.add_argument("--spec-file", required=True, help="Path to project spec YAML")
    parser.add_argument("--data-dir", default="kb/01-chats-input-organized", help="Root of organized data")
    parser.add_argument("--output-dir", default="kb/03-missing-periods", help="Where to save gap reports")
    parser.add_argument("--high-threshold", default="12h", help="Threshold for high sensitivity")
    parser.add_argument("--low-threshold", default="2d", help="Threshold for low sensitivity")
    return parser.parse_args()

def parse_duration(duration_str):
    match = re.match(r"(\d+)([hd])", duration_str.lower())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'h': return timedelta(hours=value)
    if unit == 'd': return timedelta(days=value)
    return timedelta(0)

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def is_functional_line(line: str) -> bool:
    line = line.strip()
    if not line: return True
    if line.startswith('---'): return True
    if line.startswith('# --'): return True
    if line.startswith('-- 20'): return True
    if line.startswith('title:') or line.startswith('date '): return True
    if line.startswith('group:') or line.startswith('month:'): return True
    if line.startswith('last_updated:'): return True
    return False

def get_pure_message_context(lines, start_idx, direction='backward', count=3):
    """
    IMPLEMENTATION LOGIC:
    This function extracts searchable 'Connection Points' for human collectors.
    
    For a gap detected at 'time_tag_B' (the return point):
    - 'after': Move UP from 'time_tag_B' to find what messages we already have right before the gap in the FILE.
    - 'before': Move DOWN from 'time_tag_B' to find what messages start our next available data segment.
    """
    result = []
    curr = start_idx - 1 if direction == 'backward' else start_idx + 1
    
    while len(result) < count:
        if curr < 0 or curr >= len(lines):
            break
        
        line = lines[curr].strip()
        if not is_functional_line(line):
            result.append(line)
            
        if direction == 'backward':
            curr -= 1
        else:
            curr += 1
            
    if direction == 'backward':
        result.reverse()
        
    return LiteralStr("\n".join(result)) if result else "N/A"

def extract_time_tags_from_source(source_dir, start_dt, end_dt):
    time_tags = []
    source_path = Path(source_dir)
    if not source_path.exists(): return time_tags

    p_std = re.compile(r'^--\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})')

    for md_file in sorted(source_path.glob("*.md")):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for idx, line in enumerate(lines):
                    line_content = line.strip()
                    m = p_std.match(line_content)
                    if m:
                        dt_str = f"{m.group(1)} {m.group(2)}"
                        try:
                            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                            if start_dt <= dt <= end_dt:
                                time_tags.append({
                                    "dt": dt,
                                    "file": md_file.name,
                                    "idx": idx,
                                    "raw": line_content,
                                    "all_lines": lines
                                })
                        except ValueError: pass
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)

    time_tags.sort(key=lambda x: (x['dt'], x['file'], x['idx']))
    return time_tags

def find_gaps_with_sandwich_context(time_tags, start_dt, end_dt, threshold_td):
    """
    LOGIC: 'after' and 'before' contexts are centered around the 'resume point' (nxt tag).
    This creates a clear boundary for where the data is missing in the IM history.
    """
    gaps = []

    if not time_tags:
        gaps.append({
            "after": "START OF PROJECT RANGE",
            "after_time": "N/A",
            "missing": [start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")],
            "before_time": "N/A",
            "before": "END OF PROJECT RANGE"
        })
        return gaps

    # 1. Start boundary gap
    if (time_tags[0]['dt'] - start_dt) > threshold_td:
        gaps.append({
            "after": "START OF PROJECT RANGE",
            "after_time": f"Expect: {start_dt.strftime('%Y-%m-%d %H:%M')}",
            "missing": [start_dt.strftime("%Y-%m-%d %H:%M"), (time_tags[0]['dt'] - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")],
            "before_time": time_tags[0]['raw'],
            "before": get_pure_message_context(time_tags[0]['all_lines'], time_tags[0]['idx'], 'forward', 3)
        })

    # 2. Internal gaps
    for i in range(len(time_tags) - 1):
        curr = time_tags[i]
        nxt = time_tags[i+1]
        
        if (nxt['dt'] - curr['dt']) > threshold_td:
            # Pivot Point is nxt (where we find data again)
            gaps.append({
                "after": get_pure_message_context(nxt['all_lines'], nxt['idx'], 'backward', 3),
                "after_time": curr['raw'],
                "missing": [(curr['dt'] + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"), (nxt['dt'] - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")],
                "before_time": nxt['raw'],
                "before": get_pure_message_context(nxt['all_lines'], nxt['idx'], 'forward', 3)
            })

    # 3. End boundary gap
    if (end_dt - time_tags[-1]['dt']) > threshold_td:
        gaps.append({
            "after": get_pure_message_context(time_tags[-1]['all_lines'], time_tags[-1]['idx'], 'backward', 3),
            "after_time": time_tags[-1]['raw'],
            "missing": [(time_tags[-1]['dt'] + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")],
            "before_time": f"Expect: {end_dt.strftime('%Y-%m-%d %H:%M')}",
            "before": "END OF PROJECT RANGE"
        })

    return gaps

def main():
    args = parse_args()
    high_td = parse_duration(args.high_threshold)
    low_td = parse_duration(args.low_threshold)

    try:
        spec = load_yaml(args.spec_file)
    except Exception as e:
        print(f"Error loading spec: {e}"); sys.exit(1)

    project_id = spec['meta']['id']
    time_range = spec['scope']['time_range']
    start_dt = datetime.strptime(time_range['start'], "%Y-%m-%d")
    end_dt = datetime.strptime(time_range.get('end', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").replace(hour=23, minute=59)

    report = {
        "meta": {
            "name": "check gap",
            "description": "检查 chat 的 gap，输出每个 chat 的 gap 情况。",
            "high_sensitivity_threshold": args.high_threshold,
            "low_sensitivity_threshold": args.low_threshold,
            "property_definitions": {
                "after": "缺失区间之前最后的几行原始消息（从恢复点向上扫描 3 行，排除功能标记）",
                "after_time": "缺失区间开始前最后一个时间标签",
                "missing": "[缺失开始, 缺失结束] 时间范围",
                "before_time": "数据恢复点的第一个时间标签",
                "before": "数据恢复后的前几行原始消息（从恢复点向下扫描 3 行，排除功能标记）"
            }
        },
        "results": []
    }

    for src in spec['scope']['sources']:
        src_name = src['name'] if isinstance(src, dict) else src
        sensitivity = src.get('time_sensitivity', 'low') if isinstance(src, dict) else 'low'
        threshold_td = high_td if sensitivity == 'high' else low_td

        print(f"Scanning source: {src_name} (Sensitivity: {sensitivity})...")
        sanitized_name = RegexPatterns.chat_name_sanitize(src_name)
        source_path = Path(args.data_dir) / sanitized_name

        time_tags = extract_time_tags_from_source(source_path, start_dt, end_dt)
        unique_days = set(t['dt'].date() for t in time_tags)
        total_days_expected = (end_dt.date() - start_dt.date()).days + 1
        coverage_pct = (len(unique_days) / total_days_expected) * 100 if total_days_expected > 0 else 0

        gaps = find_gaps_with_sandwich_context(time_tags, start_dt, end_dt, threshold_td)
        status = "正常"
        if not source_path.exists() or not time_tags: status = "缺失"
        elif gaps: status = "部分缺失"

        report["results"].append({
            "chat": src_name,
            "exists": source_path.exists(),
            "time_sensitivity": sensitivity,
            "status": status,
            "data_status": [
                {
                    "days_found": len(unique_days),
                    "days_expected": total_days_expected,
                    "days_coverage": f"{coverage_pct:.2f}%",
                    "missing": gaps
                }
            ]
        })

    out_dir = Path(args.output_dir)
    if not out_dir.exists(): out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_file = out_dir / f"missing_{project_id}_{timestamp}.yaml"

    with open(out_file, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, allow_unicode=True, sort_keys=False)
    print(f"Detailed sandwich-context gap report saved to {out_file}")

if __name__ == "__main__":
    main()
