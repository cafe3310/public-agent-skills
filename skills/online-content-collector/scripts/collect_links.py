import os
import re
import datetime
import argparse
import yaml

def collect_links(args):
    search_root = args.vault_path
    list_dir_full = args.list_dir
    
    if not os.path.isdir(search_root):
        print(f"错误：Vault 路径不存在 - {search_root}")
        return

    # Pattern to catch markers: #Marker-待下载, #Marker-下载中-YYYYMMDDHH, etc.
    # We want to capture the status and the optional suffix (like -演示)
    marker_pattern = re.compile(r'#Marker-(待下载|下载中|下载失败)(-[^\s\n]*?)?(-\d{10,})?(\s|$)')
    time_pattern = re.compile(r'time:\s*`?\s*([^`\s\n][^`\n]*[^`\s\n])\s*`?')
    source_pattern = re.compile(r'source:\s*`?\s*([^`\s\n][^`\n]*[^`\s\n])\s*`?')
    
    found_items = []
    now_stamp = datetime.datetime.now().strftime('%Y%m%d%H')
    
    for root, dirs, files in os.walk(search_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'skills' and d != 'node_modules']
        for file in files:
            if not file.endswith('.md'):
                continue
            
            filepath = os.path.join(root, file)
            if list_dir_full and list_dir_full in filepath:
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            file_changed = False
            new_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                # Search for marker in current line
                match = marker_pattern.search(line)
                if match:
                    item_time = "Unknown"
                    item_source = None
                    
                    # Look ahead for metadata
                    for j in range(1, 6):
                        if i + j < len(lines):
                            t_match = time_pattern.search(lines[i+j])
                            s_match = source_pattern.search(lines[i+j])
                            if t_match: item_time = t_match.group(1)
                            if s_match: item_source = s_match.group(1)
                    
                    if item_source:
                        url = item_source.strip().strip('`').strip()
                        if not url.startswith('http'):
                            url = 'https://' + url
                            
                        # Determine the base tag (e.g. #Marker-待下载-演示)
                        status_type = match.group(1) # 待下载 or 下载中 or 下载失败
                        suffix = match.group(2) or "" # -演示
                        
                        # Clean up suffix
                        clean_suffix = re.sub(r'^-+', '-', suffix)
                        clean_suffix = re.sub(r'-+$', '', clean_suffix)
                        
                        base_tag = f"#Marker-待下载{clean_suffix}"
                        
                        found_items.append({
                            'date': item_time,
                            'tag_type': base_tag,
                            'url': url,
                            'source_file': os.path.relpath(filepath, search_root),
                            'status': '待处理'
                        })
                        
                        # Update line to #Marker-下载中-{suffix}-{now_stamp}
                        new_marker = f"#Marker-下载中{clean_suffix}-{now_stamp}"
                        # Replace the old marker with the new one
                        line = line.replace(match.group(0).strip(), new_marker)
                        file_changed = True
                
                new_lines.append(line)
                i += 1
            
            if file_changed:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
    
    if not found_items:
        print("未发现待处理的链接。")
        return

    now = datetime.datetime.now()
    list_filename = f"{now.strftime('%Y-%m-%d-%H')} 下载列表整理.md"
    os.makedirs(list_dir_full, exist_ok=True)
    list_path = os.path.join(list_dir_full, list_filename)
    
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(f"# 下载列表整理 ({now.strftime('%Y-%m-%d %H:%M')})\n\n")
        f.write("```yaml\n")
        yaml.dump(found_items, f, allow_unicode=True, sort_keys=False)
        f.write("```\n")
    
    print(f"成功收集 {len(found_items)} 条链接，列表已生成：{list_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault-path", required=True)
    parser.add_argument("--list-dir", required=True)
    args = parser.parse_args()
    collect_links(args)
