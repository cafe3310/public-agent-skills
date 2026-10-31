import os
import sys
import shutil
import datetime
import argparse

def count_lines(file_path):
    """Count lines in a file, ignoring encoding errors."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"Error counting lines in {file_path}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Initialize the audio transcript processing workspace.")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='Source transcript files to process')
    parser.add_argument('-s', '--segment-size', type=int, default=100, help='Number of lines per segment (default: 100)')
    args = parser.parse_args()

    # 1. Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(script_dir)
    assets_dir = os.path.join(skill_root, 'assets')
    
    # 2. Create workspace directory
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M")
    base_dir = f"语音转写处理_{timestamp}"
    
    if os.path.exists(base_dir):
        print(f"Directory {base_dir} already exists. Please handle manually.")
        sys.exit(1)

    os.makedirs(base_dir)
    print(f"Created workspace: {base_dir}")

    # 3. Create subdirectories
    dirs = {
        "1-原始文件": os.path.join(base_dir, "1-原始文件"),
        "2-要求和信息": os.path.join(base_dir, "2-要求和信息"),
        "5-最终输出": os.path.join(base_dir, "5-最终输出")
    }
    for d in dirs.values():
        os.makedirs(d)

    # 4. Copy source files and prepare file info
    source_files_info = []
    for src_file in args.files:
        if not os.path.exists(src_file):
            print(f"Warning: File {src_file} not found. Skipping.")
            continue
        
        filename = os.path.basename(src_file)
        dest_path = os.path.join(dirs["1-原始文件"], filename)
        shutil.copy2(src_file, dest_path)
        
        total_lines = count_lines(dest_path)
        source_files_info.append({"name": filename, "total_lines": total_lines})
        print(f"Copied {filename} ({total_lines} lines) to 1-原始文件/")

    if not source_files_info:
        print("Error: No valid source files provided.")
        shutil.rmtree(base_dir)
        sys.exit(1)

    # 5. Initialize context documents from assets
    templates_mapping = {
        'proofreading_glossary_template.md': '3-校对和术语表.md',
        'segment_topics_template.md': '4-分段主题.md',
        'speaker_info_template.md': '2-要求和信息/发言人信息.md'
    }

    for t_name, out_name in templates_mapping.items():
        src = os.path.join(assets_dir, t_name)
        dest = os.path.join(base_dir, out_name)
        if os.path.exists(src):
            shutil.copy2(src, dest)
            print(f"Initialized {out_name}")

    # 6. Generate 0-工作日志.md from template
    log_template_path = os.path.join(assets_dir, 'work_log_template.md')
    log_output_path = os.path.join(base_dir, '0-工作日志.md')
    
    if os.path.exists(log_template_path):
        with open(log_template_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Replace date
        log_content = log_content.replace('{{DATE}}', timestamp)
        
        # Build segments list
        segments_list = []
        for info in source_files_info:
            segments_list.append(f"- {info['name']} (Total lines: {info['total_lines']})")
            start = 1
            while start <= info['total_lines']:
                end = min(start + args.segment_size - 1, info['total_lines'])
                segments_list.append(f"  - [ ] {start}-{end}")
                start += args.segment_size
            segments_list.append("") # Spacer
        
        # Insert segments
        marker = "## 任务来源文件和分段(按顺序)"
        if marker in log_content:
            parts = log_content.split(marker)
            # Replace the placeholder part after the marker
            # We keep the header and everything before it, then append our new list
            new_log_content = parts[0] + marker + "\n\n> 追踪每个文件的处理进度。使用 `[x]` 标记已完成，`[ ]` 标记待处理。\n\n" + "\n".join(segments_list)
            log_content = new_log_content

        with open(log_output_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        print(f"Initialized work log: {log_output_path}")

    print("\nNext steps:")
    print(f"1. Add background info and refine speaker info in {dirs['2-要求和信息']}")
    print(f"2. Begin processing loop using {log_output_path}")

if __name__ == "__main__":
    main()
    
    print(f"Initialized work log")
    print("\nNext steps:")
    print(f"1. Add background info")
    print(f"2. Begin processing loop using work log")
