import os
import sys
import shutil
import datetime
import argparse

def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return sum(1 for _ in f)

def main():
    parser = argparse.ArgumentParser(description="Initialize the audio transcript processing workspace.")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='Source transcript files to process')
    args = parser.parse_args()

    # 1. Create directory
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    base_dir = f"语音转写处理_{timestamp}"
    
    if os.path.exists(base_dir):
        print(f"Directory {base_dir} already exists. Please handle manually or wait a minute.")
        return

    os.makedirs(base_dir)
    print(f"Created workspace: {base_dir}")

    # 2. Create subdirectories
    dir_1 = os.path.join(base_dir, "1-原始文件")
    dir_2 = os.path.join(base_dir, "2-要求和信息")
    dir_5 = os.path.join(base_dir, "5-最终输出")
    
    os.makedirs(dir_1)
    os.makedirs(dir_2)
    os.makedirs(dir_5)

    # Copy source files
    source_files = []
    for src_file in args.files:
        if not os.path.exists(src_file):
            print(f"Error: File {src_file} not found.")
            continue
        
        filename = os.path.basename(src_file)
        dest_path = os.path.join(dir_1, filename)
        shutil.copy2(src_file, dest_path)
        source_files.append(filename)
        print(f"Copied {filename} to {dir_1}")

    # 3. Create context docs from assets
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(script_dir), 'assets')
    
    # Try to copy assets if they exist, otherwise create default content
    glossary_src = os.path.join(assets_dir, 'proofreading_glossary_template.md')
    if os.path.exists(glossary_src):
        shutil.copy2(glossary_src, os.path.join(base_dir, '3-校对和术语表.md'))
    else:
        with open(os.path.join(base_dir, '3-校对和术语表.md'), 'w') as f:
            f.write("# 校对和术语表\n\n## 术语表\n\n## 常见错误与修正\n")

    topics_src = os.path.join(assets_dir, 'segment_topics_template.md')
    if os.path.exists(topics_src):
        shutil.copy2(topics_src, os.path.join(base_dir, '4-分段主题.md'))
    else:
        with open(os.path.join(base_dir, '4-分段主题.md'), 'w') as f:
            f.write("# 分段主题记录\n\n> 在此记录每个已处理分段的核心主题。\n")

    # 4. Create 0-工作日志.md with plan
    log_path = os.path.join(base_dir, '0-工作日志.md')
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        # Write header
        log_file.write("# 工作日志\n\n")
        log_file.write(f"创建时间: {timestamp}\n\n")
        
        log_file.write("## 任务来源文件和分段(按顺序)\n\n")
        log_file.write("> 示例：\n")
        log_file.write("> - filename.txt\n")
        log_file.write(">   - [x] 1-200 (2024-01-01 12:00)\n")
        log_file.write(">   - [ ] 201-400\n\n")
        
        SEGMENT_SIZE = 200
        
        for filename in source_files:
            file_path = os.path.join(dir_1, filename)
            total_lines = count_lines(file_path)
            log_file.write(f"- {filename} (Total lines: {total_lines})\n")
            
            start = 1
            while start <= total_lines:
                end = min(start + SEGMENT_SIZE - 1, total_lines)
                log_file.write(f"  - [ ] {start}-{end}\n")
                start += SEGMENT_SIZE
    
    print(f"Initialized work log: {log_path}")
    print("\nNext steps:")
    print(f"1. Add background info to {dir_2}")
    print(f"2. Begin processing loop using {log_path}")

if __name__ == "__main__":
    main()
