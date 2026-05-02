import os
import sys
import shutil
import datetime
import argparse
import re

def parse_markdown_structure(file_path):
    """
    Parses a markdown file to find headers and their line ranges.
    Returns a list of dicts: {'title': str, 'level': int, 'start': int, 'end': int}
    """
    structure = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            # Stack to keep track of active sections at different levels
            # Each element: {'level': int, 'index': int} pointing to structure list
            active_sections = []
            
            for i, line in enumerate(lines):
                line_num = i + 1
                # Match headers: # Title, ## Title, etc.
                match = re.match(r'^(#+)\s+(.*)', line)
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    
                    # Close any open sections that are >= this new level
                    # (Lower level number means higher hierarchy, e.g., # is level 1)
                    while active_sections and structure[active_sections[-1]['index']]['level'] >= level:
                        idx = active_sections.pop()['index']
                        structure[idx]['end'] = line_num - 1
                    
                    # Also, the immediately preceding section (regardless of level) *might* end here
                    # if it wasn't closed above. But the logic above handles hierarchy.
                    # For flat lists or "jumping back up", we simply close what's necessary.
                    # Actually, a safer bet for a simple list is:
                    # If there is *any* previous section that hasn't ended, and it's not a parent of this one...
                    # But simpler logic: The previous header's section ends right before this one starts,
                    # UNLESS we want to support nested "containment" in the line ranges.
                    #
                    # "TOC style" usually implies that Section 1 ends where Section 2 begins.
                    # Let's enforce that: The *immediately previous* item in the structure list ends here,
                    # if it hasn't ended yet.
                    if structure and structure[-1]['end'] == -1:
                         structure[-1]['end'] = line_num - 1

                    # Add new section
                    structure.append({
                        'title': title,
                        'level': level,
                        'start': line_num,
                        'end': -1 # Placeholder
                    })
                    
                    # Track this section index to update its end later
                    active_sections.append({'level': level, 'index': len(structure) - 1})
                    
            # Close all remaining open sections at EOF
            for item in active_sections:
                structure[item['index']]['end'] = total_lines
            
            # Catch-all for flat structure if stack logic missed anything
            if structure and structure[-1]['end'] == -1:
                structure[-1]['end'] = total_lines
                
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return [], 0
    
    return structure, total_lines

def main():
    parser = argparse.ArgumentParser(description="Initialize the chat log projectization workspace.")
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='Source chat log files to process')
    args = parser.parse_args()

    # 1. Create directory
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    base_dir = f"Chat_Projectization_{timestamp}"
    
    if os.path.exists(base_dir):
        print(f"Directory {base_dir} already exists. Please handle manually or wait a minute.")
        return

    os.makedirs(base_dir)
    print(f"Created workspace: {base_dir}")

    # 2. Create subdirectories
    dir_1 = os.path.join(base_dir, "1-原始记录")
    dir_2 = os.path.join(base_dir, "2-项目背景")
    dir_6 = os.path.join(base_dir, "6-最终输出")
    
    os.makedirs(dir_1)
    os.makedirs(dir_2)
    os.makedirs(dir_6)

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

    # 3. Create context docs (placeholders)
    # 3-实体映射表.md
    with open(os.path.join(base_dir, '3-实体映射表.md'), 'w', encoding='utf-8') as f:
         f.write("# 实体映射表\n\n## 人物映射\n- 昵称/代号 -> 真实角色/职责\n\n## 项目代号\n- 代号 -> 项目全称/描述\n")
    
    # 4-任务池.md
    with open(os.path.join(base_dir, '4-任务池.md'), 'w', encoding='utf-8') as f:
         f.write("# 任务池 (Task Pool)\n\n## 待处理 (TODO)\n\n## 进行中 (IN PROGRESS)\n\n## 已完成 (DONE)\n\n## 待确认 (UNCONFIRMED)\n")

    # 5-决策与里程碑.md
    with open(os.path.join(base_dir, '5-决策与里程碑.md'), 'w', encoding='utf-8') as f:
         f.write("# 决策与里程碑\n\n## 关键决策\n\n## 里程碑时间线\n")

    # 4. Create 0-工作日志.md with TOC-based plan
    log_path = os.path.join(base_dir, '0-工作日志.md')
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write("# 工作日志\n\n")
        log_file.write(f"创建时间: {timestamp}\n\n")
        log_file.write("## 执行策略\n")
        log_file.write("- 分段策略: 基于 Markdown 标题 (TOC)\n")
        log_file.write("- 重点关注: 任务分配、时间节点、决策结论\n")
        log_file.write("- 注意事项: 请严格按照下方列表顺序，逐个处理 Section。\n\n")
        log_file.write("## 任务分段列表\n\n")
        
        for filename in source_files:
            file_path = os.path.join(dir_1, filename)
            log_file.write(f"### 文件: {filename}\n\n")
            
            structure, total_lines = parse_markdown_structure(file_path)
            
            if not structure:
                 log_file.write(f"- [ ] 全文 (Line 1-{total_lines}) [未检测到标题]\n")
            else:
                for section in structure:
                    # Limit indentation to reasonable levels for readability
                    indent_level = max(0, section['level'] - 1)
                    indent = "  " * indent_level
                    
                    # Format: - [ ] <Header Title> (Line start-end)
                    log_file.write(f"{indent}- [ ] **{section['title']}** (Line {section['start']}-{section['end']})\n")

    print(f"Initialized work log: {log_path}")
    print("\nNext steps:")
    print(f"1. Add background docs to {dir_2}")
    print(f"2. Check '0-工作日志.md' to see the generated task list")
    print(f"3. Begin processing loop section by section")

if __name__ == "__main__":
    main()
