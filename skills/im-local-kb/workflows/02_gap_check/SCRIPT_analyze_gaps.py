import os
import argparse
import yaml
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the workflows/01_ingest directory to sys.path to import SCRIPT_util
sys.path.append(str(Path(__file__).parent.parent / "01_ingest"))
from SCRIPT_util import RegexPatterns

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze data gaps in chat logs with precise search context.")
    parser.add_argument("--spec-file", required=True, help="Path to project spec YAML")
    parser.add_argument("--data-dir", default="kb/01-chats-input-organized", help="Root of organized data")
    parser.add_argument("--output-dir", default="kb/03-missing-periods", help="Where to save gap reports")
    parser.add_argument("--high-threshold", default="12h", help="Threshold for high sensitivity (e.g., 12h)")
    parser.add_argument("--low-threshold", default="2d", help="Threshold for low sensitivity (e.g., 2d)")
    return parser.parse_args()

def parse_duration(duration_str):
    match = re.match(r"(\d+)([hd])", duration_str.lower())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    return timedelta(0)

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_non_blank_context(lines, start_idx, direction='backward', count=3):
    """
    Helper to find N non-blank lines in a specific direction.
    direction='backward': searches from start_idx upwards (inclusive of start_idx).
    direction='forward': searches from start_idx downwards (inclusive of start_idx).
    """
    result = []
    curr = start_idx
    
    while len(result) < count:
        if curr < 0 or curr >= len(lines):
            break
        
        line = lines[curr].strip()
        if line:
            result.append(line)
            
        if direction == 'backward':
            curr -= 1
        else:
            curr += 1
            
    if direction == 'backward':
        result.reverse()
        
    return "\n".join(result)

def extract_time_tags_from_source(source_dir, start_dt, end_dt):
    """
    Scans all .md files and extracts time tags with the ability to retrieve original file lines for context.
    """
    time_tags = []
    source_path = Path(source_dir)

    if not source_path.exists():
        return time_tags

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
                                # We store the lines and index to perform the "look back/forward non-blank" logic later
                                time_tags.append({
                                    "dt": dt,
                                    "file": md_file.name,
                                    "idx": idx,
                                    "raw": line_content,
                                    "all_lines": lines # Reference to the file content
                                })
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)

    time_tags.sort(key=lambda x: x['dt'])
    return time_tags

def find_gaps_with_precise_context(time_tags, start_dt, end_dt, threshold_td):
    """
    Implementation Strategy for Search Anchors:
    
    1. For each gap identified between Tag[i] and Tag[i+1]:
       - 'after_these_lines': Represents the 'departure point'. 
         Logic: Start from Tag[i], look BACKWARD to collect 3 non-blank lines (including the Tag line).
       - 'before_these_lines': Represents the 'return point'.
         Logic: Start from Tag[i+1], look FORWARD to collect 3 non-blank lines (including the Tag line).
         
    2. This allows the user to search for the specific messages in their IM client to identify 
       exactly where the batch copy-paste should begin and end.
    """
    gaps = []

    if not time_tags:
        gaps.append({
            "after_these_lines": "START OF PROJECT RANGE",
            "after_these_time_tag": "N/A",
            "missing_interval": [start_dt.strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")],
            "before_these_time_tag": "N/A",
            "before_these_lines": "END OF PROJECT RANGE"
        })
        return gaps

    # 1. Start boundary gap
    if (time_tags[0]['dt'] - start_dt) > threshold_td:
        gaps.append({
            "after_these_lines": "START OF PROJECT RANGE",
            "after_these_time_tag": f"Expect: {start_dt.strftime('%Y-%m-%d %H:%M')}",
            "missing_interval": [start_dt.strftime("%Y-%m-%d %H:%M"), (time_tags[0]['dt'] - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")],
            "before_these_time_tag": time_tags[0]['raw'],
            "before_these_lines": get_non_blank_context(time_tags[0]['all_lines'], time_tags[0]['idx'], 'forward', 3)
        })

    # 2. Internal gaps
    for i in range(len(time_tags) - 1):
        curr = time_tags[i]
        nxt = time_tags[i+1]
        
        if (nxt['dt'] - curr['dt']) > threshold_td:
            # Plan: after_these_lines = Context ending AT curr tag
            #       before_these_lines = Context starting AT nxt tag
            gaps.append({
                "after_these_lines": get_non_blank_context(curr['all_lines'], curr['idx'], 'backward', 3),
                "after_these_time_tag": curr['raw'],
                "missing_interval": [(curr['dt'] + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"), (nxt['dt'] - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")],
                "before_these_time_tag": nxt['raw'],
                "before_these_lines": get_non_blank_context(nxt['all_lines'], nxt['idx'], 'forward', 3)
            })

    # 3. End boundary gap
    if (end_dt - time_tags[-1]['dt']) > threshold_td:
        gaps.append({
            "after_these_lines": get_non_blank_context(time_tags[-1]['all_lines'], time_tags[-1]['idx'], 'backward', 3),
            "after_these_time_tag": time_tags[-1]['raw'],
            "missing_interval": [(time_tags[-1]['dt'] + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"), end_dt.strftime("%Y-%m-%d %H:%M")],
            "before_these_time_tag": f"Expect: {end_dt.strftime('%Y-%m-%d %H:%M')}",
            "before_these_lines": "END OF PROJECT RANGE"
        })

    return gaps

def main():
    args = parse_args()
    high_td = parse_duration(args.high_threshold)
    low_td = parse_duration(args.low_threshold)

    try:
        spec = load_yaml(args.spec_file)
    except Exception as e:
        print(f"Error loading spec: {e}")
        sys.exit(1)

    project_id = spec['meta']['id']
    time_range = spec['scope']['time_range']
    start_dt = datetime.strptime(time_range['start'], "%Y-%m-%d")
    end_dt = datetime.strptime(time_range.get('end', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").replace(hour=23, minute=59)

    report = {
        "meta": {
            "name": "check gap",
            "description": "检查 chat 的 gap，输出每个 chat 的 gap 情况。",
            "high_sensitivity_threshold": args.high_threshold,
            "high_sensitivity_threshold_desc": f"如果上一个 time tag 和下一个间隔 {args.high_threshold} 以上认为中间有缺失",
            "low_sensitivity_threshold": args.low_threshold,
            "low_sensitivity_threshold_desc": f"如果上一个 time tag 和下一个间隔 {args.low_threshold} 以上认为中间有缺失"
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

        exists = source_path.exists()
        time_tags = extract_time_tags_from_source(source_path, start_dt, end_dt)
        
        unique_days = set(t['dt'].date() for t in time_tags)
        total_days_expected = (end_dt.date() - start_dt.date()).days + 1
        coverage_pct = (len(unique_days) / total_days_expected) * 100 if total_days_expected > 0 else 0

        gaps = find_gaps_with_precise_context(time_tags, start_dt, end_dt, threshold_td)
        
        status = "正常"
        if not exists or not time_tags: status = "缺失"
        elif gaps: status = "部分缺失"

        report["results"].append({
            "chat": src_name,
            "exists": exists,
            "time_sensitivity": sensitivity,
            "status": status,
            "data_status": [
                {
                    "days_found": len(unique_days),
                    "days_expected": total_days_expected,
                    "days_coverage": f"{coverage_pct:.2f}%",
                    "missing_intervals": gaps
                }
            ]
        })

    out_dir = Path(args.output_dir)
    if not out_dir.exists(): out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_file = out_dir / f"missing_{project_id}_{timestamp}.yaml"

    with open(out_file, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, allow_unicode=True, sort_keys=False)
    print(f"Detailed gap report with search anchors saved to {out_file}")

if __name__ == "__main__":
    main()
