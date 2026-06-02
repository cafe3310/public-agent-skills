import argparse
import os
import glob
import yaml
from datetime import datetime

def analyze_files(keywords, directory, context_lines):
    # 1. 创建临时目录
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    tmp_dir_name = f"tmp-{timestamp}-analysis"
    # 创建在 CWD, 而非 directory
    tmp_dir_path = os.path.join(os.getcwd(), tmp_dir_name)
    os.makedirs(tmp_dir_path, exist_ok=True)
    print(tmp_dir_path) # 将路径输出到 stdout

    # 2. 搜索与分析文件
    all_files_data = []
    # 使用 glob 递归搜索 .md 文件
    for filepath in glob.iglob(os.path.join(directory, '**', '*.md'), recursive=True):
        # 排除特定目录
        path_parts = filepath.split(os.path.sep)
        if any(part.startswith('tmp-') for part in path_parts) or '_attachments' in path_parts or '.trash' in path_parts:
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError):
            continue

        keyword_locations = {kw: [] for kw in keywords}
        has_keywords = False
        for i, line in enumerate(lines):
            for kw in keywords:
                if kw in line:
                    keyword_locations[kw].append(i)
                    has_keywords = True
        
        if not has_keywords:
            continue

        # 3. 计算关键词频率
        keyword_counts = []
        for kw, locs in keyword_locations.items():
            if locs:
                keyword_counts.append({'word': kw, 'count': len(locs)})

        # 4. 合并上下文行区间
        all_keyword_lines = sorted(list(set(line for locs in keyword_locations.values() for line in locs)))
        
        if not all_keyword_lines:
            continue
            
        line_ranges = []
        start = max(0, all_keyword_lines[0] - context_lines)
        end = min(len(lines) - 1, all_keyword_lines[0] + context_lines)
        
        for line_num in all_keyword_lines[1:]:
            current_start = max(0, line_num - context_lines)
            if current_start > end + 1:
                line_ranges.append([start, end])
                start = current_start
            
            end = min(len(lines) - 1, line_num + context_lines)
        
        line_ranges.append([start, end])

        # 5. 存储文件数据
        file_data = {
            'file_path': os.path.relpath(filepath, os.getcwd()),
            'keyword_counts': keyword_counts,
            'line_ranges': line_ranges
        }
        all_files_data.append(file_data)

    # 6. 写入 YAML 文件
    yaml_path = os.path.join(tmp_dir_path, '001_analysis.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(all_files_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Search and analyze markdown files for keywords.")
    parser.add_argument('--keywords', nargs='+', required=True, help='List of keywords to search for.')
    parser.add_argument('--directory', required=True, help='The root directory of the knowledge base.')
    parser.add_argument('--context-lines', type=int, default=10, help='Number of lines to include before and after a keyword match for context merging.')
    
    args = parser.parse_args()
    
    analyze_files(args.keywords, args.directory, args.context_lines)
