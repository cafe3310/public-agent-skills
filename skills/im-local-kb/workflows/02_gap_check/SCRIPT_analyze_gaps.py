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
    parser = argparse.ArgumentParser(description="Analyze data gaps in chat logs.")
    parser.add_argument("--spec-file", required=True, help="Path to project spec YAML")
    parser.add_argument("--data-dir", default="kb/01-chats-input-organized", help="Root of organized data")
    parser.add_argument("--output-dir", default="kb/03-missing-periods", help="Where to save gap reports")
    parser.add_argument("--threshold-days", type=int, default=3, help="Max allowed gap in days")
    return parser.parse_args()

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_dates_from_source(source_dir, start_date, end_date):
    """
    Scans all .md files in the source directory and extracts unique dates from lines.
    Supports formats:
    - ## [YYYY-MM-DD]
    - -- YYYY-MM-DD
    - -- MM-DD
    """
    found_dates = set()
    source_path = Path(source_dir)

    if not source_path.exists():
        return sorted(list(found_dates))

    # 支持多种日期格式的正则
    # 模式 1: ## [YYYY-MM-DD]
    p1 = re.compile(r'^##\s+\[(\d{4}-\d{2}-\d{2})\]')
    # 模式 2: -- YYYY-MM-DD
    p2 = re.compile(r'^--\s*(\d{4}-\d{2}-\d{2})')
    # 模式 3: -- MM-DD
    p3 = re.compile(r'^--\s*(\d{2}-\d{2})')

    for md_file in source_path.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    dt = None

                    m1 = p1.match(line)
                    if m1:
                        dt = datetime.strptime(m1.group(1), "%Y-%m-%d")
                    else:
                        m2 = p2.match(line)
                        if m2:
                            dt = datetime.strptime(m2.group(1), "%Y-%m-%d")
                        else:
                            m3 = p3.match(line)
                            if m3:
                                today = datetime.now()
                                try:
                                    dt = datetime.strptime(m3.group(1), "%m-%d")
                                    dt = dt.replace(year=today.year)
                                except ValueError:
                                    pass

                    if dt and start_date <= dt <= end_date:
                        found_dates.add(dt)
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)

    return sorted(list(found_dates))

def find_gaps(dates, start_date, end_date, threshold_days):
    """
    Identify missing intervals in a list of dates.
    """
    gaps = []

    # 1. Check start boundary
    if not dates:
        gaps.append(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} (NO DATA)")
        return gaps

    if (dates[0] - start_date).days > threshold_days:
        gaps.append(f"{start_date.strftime('%Y-%m-%d')} ~ {(dates[0] - timedelta(days=1)).strftime('%Y-%m-%d')}")

    # 2. Check internal gaps
    for i in range(len(dates) - 1):
        current = dates[i]
        next_day = dates[i+1]
        delta = (next_day - current).days
        if delta > threshold_days + 1: # e.g. 1st and 5th (delta=4), gap is 2nd,3rd,4th
             gap_start = current + timedelta(days=1)
             gap_end = next_day - timedelta(days=1)
             gaps.append(f"{gap_start.strftime('%Y-%m-%d')} ~ {gap_end.strftime('%Y-%m-%d')}")

    # 3. Check end boundary
    if (end_date - dates[-1]).days > threshold_days:
        gaps.append(f"{(dates[-1] + timedelta(days=1)).strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

    return gaps

def main():
    args = parse_args()

    # Load Spec
    print(f"Loading spec from {args.spec_file}...")
    try:
        spec = load_yaml(args.spec_file)
    except Exception as e:
        print(f"Error loading spec: {e}")
        sys.exit(1)

    project_id = spec['meta']['id']
    time_range = spec['scope']['time_range']
    start_date = datetime.strptime(time_range['start'], "%Y-%m-%d")

    # Use current date if 'end' is not specified
    if 'end' in time_range:
        end_date = datetime.strptime(time_range['end'], "%Y-%m-%d")
    else:
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    sources = spec['scope']['sources']

    report = {
        "project_id": project_id,
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "OK",
        "missing_details": []
    }

    has_missing = False

    for src in sources:
        # Handle source object or string
        src_name = src['name'] if isinstance(src, dict) else src

        # Determine strictness
        # Default to 'low' unless specified 'high'
        # Currently the simple logic doesn't differentiate threshold, but could be extended
        # strictness = src.get('time_sensitivity', 'low') if isinstance(src, dict) else 'low'

        print(f"Scanning source: {src_name}...")

        # Sanitize name for path
        src_name = RegexPatterns.chat_name_sanitize(src_name)
        source_path = Path(args.data_dir) / src_name

        dates = extract_dates_from_source(source_path, start_date, end_date)

        # Calculate coverage simple metric
        total_days = (end_date - start_date).days + 1
        coverage_pct = (len(dates) / total_days) * 100 if total_days > 0 else 0

        gaps = find_gaps(dates, start_date, end_date, args.threshold_days)

        source_status = "OK"
        if gaps:
            source_status = "MISSING_DATA"
            has_missing = True

        report["missing_details"].append({
            "source": src_name,
            "days_found": len(dates),
            "days_expected": total_days,
            "coverage": f"{coverage_pct:.1f}%",
            "status": source_status,
            "missing_intervals": gaps
        })

    if has_missing:
        report["status"] = "INCOMPLETE"
        report["action_item"] = "请根据 missing_intervals 补充对应的 IM 记录到 00-chats-input-raw 目录。"
    else:
        report["status"] = "COMPLETE"
        report["action_item"] = "数据完整，可以进行 extract_knowledge。"

    # Save Report
    out_dir = Path(args.output_dir)
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    # Filename: missing_{project_id}.yaml (Overwrite latest)
    # Or timestamped? Instruct says "missing_proj_xxxx.yaml"
    out_file = out_dir / f"missing_{project_id}.yaml"

    with open(out_file, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, allow_unicode=True, sort_keys=False)

    print(f"Report saved to {out_file}")
    print(f"Status: {report['status']}")

if __name__ == "__main__":
    main()
