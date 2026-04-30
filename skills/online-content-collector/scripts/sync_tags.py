import os
import re
import datetime
import argparse
import yaml

def sync_tags(args):
    list_file = args.list_file
    search_root = args.vault_path
    
    if not os.path.exists(list_file):
        print(f"错误：找不到下载列表文件 {list_file}")
        return

    with open(list_file, 'r', encoding='utf-8') as f:
        content = f.read()

    yaml_match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    if not yaml_match:
        print("错误：未在列表中发现 YAML 数据块。" )
        return

    try:
        items = yaml.safe_load(yaml_match.group(1))
    except Exception as e:
        print(f"解析 YAML 失败: {str(e)}")
        return

    if not items:
        print("列表为空。" )
        return

    now_stamp = datetime.datetime.now().strftime('%Y%m%d%H')
    updated_files_count = 0

    files_to_process = {}
    for item in items:
        src = item.get('source_file')
        if src:
            if src not in files_to_process:
                files_to_process[src] = []
            files_to_process[src].append(item)

    # Marker pattern: capture the status and timestamp
    marker_pattern = re.compile(r'#Marker-(下载中)(-[^\s\n]*?)?(-\d{10})')
    source_line_pattern = re.compile(r'source:\s*`?\s*(.*?)\s*`?')

    for rel_path, file_items in files_to_process.items():
        abs_path = os.path.join(search_root, rel_path)
        if not os.path.exists(abs_path):
            print(f"警告：找不到原始文件 {abs_path}")
            continue

        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        file_changed = False
        new_lines = []
        
        for i, line in enumerate(lines):
            match = marker_pattern.search(line)
            if match:
                matched_item = None
                # Scan nearby lines for URL anchor
                for j in range(1, 6):
                    if i + j < len(lines):
                        s_match = source_line_pattern.search(lines[i+j])
                        if s_match:
                            file_url = s_match.group(1).strip().strip('`').strip()
                            for item in file_items:
                                item_url = item.get('url', '')
                                # Strict-ish match
                                if file_url in item_url or item_url in file_url:
                                    matched_item = item
                                    break
                        if matched_item: break
                
                if matched_item:
                    status = matched_item.get('status')
                    original_tag = matched_item.get('tag_type', '#Marker-待下载')
                    suffix = match.group(2) or "" # e.g. -演示
                    
                    if status == "下载完成":
                        new_marker = f"#Marker-已下载{suffix}-{now_stamp}"
                        line = line.replace(match.group(0), new_marker)
                        file_changed = True
                        print(f"  [SUCCESS] {rel_path}: {matched_item['url']} -> 已下载")
                    elif "失败" in status:
                        line = line.replace(match.group(0), original_tag)
                        file_changed = True
                        print(f"  [REVERT] {rel_path}: {matched_item['url']} -> {original_tag}")
                else:
                    print(f"  [SKIP] {rel_path} 第 {i+1} 行: 未匹配到 URL 锚点。" )
            
            new_lines.append(line)
        
        if file_changed:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            updated_files_count += 1

    print(f"同步完成。更新文件数: {updated_files_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-file", required=True)
    parser.add_argument("--vault-path", required=True)
    args = parser.parse_args()
    sync_tags(args)
