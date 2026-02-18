import argparse
import os
import yaml
import re

def extract_content(tmp_dir):
    analysis_file = os.path.join(tmp_dir, '001_analysis.yaml')
    content_file = os.path.join(tmp_dir, '002_content.yaml')

    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as e:
        print(f"Error reading or parsing {analysis_file}: {e}")
        return

    if not data:
        print("analysis.yaml is empty. No content to extract.")
        # Create an empty content file
        with open(content_file, 'w', encoding='utf-8') as f:
            yaml.dump([], f)
        return

    for item in data:
        filepath = item.get('file_path')
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)

        line_ranges = item.get('line_ranges', [])
        
        if not filepath or not line_ranges:
            item['content'] = ""
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError):
            item['content'] = f"Error: Could not read file {filepath}"
            continue

        content_parts = []
        for r in line_ranges:
            start, end = r[0], r[1]
            # Ensure start and end are within bounds
            start = max(0, start)
            end = min(len(lines), end + 1)
            
            range_content = "".join(lines[start:end])
            content_parts.append(range_content)
        
        content_str = "\n...\n".join(content_parts)

        # Clean the extracted content
        # 1. Collapse multiple newlines to a single one
        cleaned_content = re.sub(r'\n+', '\n', content_str)
        # 2. Remove markdown bold markers
        cleaned_content = cleaned_content.replace('**', '')
        # 3. Remove markdown image links
        cleaned_content = re.sub(r'!\[\[.*?\]\]', '', cleaned_content)

        item['content'] = cleaned_content

    with open(content_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"Successfully created {content_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract content from files based on analysis.yaml.")
    parser.add_argument('--tmp-dir', required=True, help='The temporary directory containing 001_analysis.yaml.')
    
    args = parser.parse_args()
    
    extract_content(args.tmp_dir)
