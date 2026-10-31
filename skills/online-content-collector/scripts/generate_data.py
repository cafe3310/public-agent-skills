import os
import json
import re
import urllib.parse

def parse_frontmatter(content):
    frontmatter = {}
    body = content
    # Match starting --- ... ---
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        body = content[match.end():]
        for line in yaml_text.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                frontmatter[key.strip()] = val.strip()
    return frontmatter, body

def scan_directory(base_dir):
    data = []
    
    # Supported media types
    img_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
    vid_exts = {'.mp4', '.mov', '.webm', '.m4v'}
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if not os.path.isdir(item_path):
            continue
            
        # Parse directory name
        # Format: [YYYY-MM-DD-hh] Category ID
        dir_pattern = r'^\[(\d{4}-\d{2}-\d{2}-\d{2})\]\s+([^\s]+)\s+(.+)$'
        match = re.match(dir_pattern, item)
        
        date_str = ""
        category = "其他"
        item_id = item
        
        if match:
            date_str = match.group(1)
            category = match.group(2)
            item_id = match.group(3)
        else:
            if not item.startswith('['):
                continue
        
        # Check files inside the directory
        files = os.listdir(item_path)
        
        md_file = None
        json_file = None
        images = []
        videos = []
        
        for file in files:
            file_path = os.path.join(item_path, file)
            if os.path.isdir(file_path):
                continue
                
            _, ext = os.path.splitext(file.lower())
            
            if ext == '.md':
                if file.startswith(item) or md_file is None:
                    md_file = file
            elif ext == '.json' and file == 'metadata.info.json':
                json_file = file
            elif ext in img_exts:
                images.append(file)
            elif ext in vid_exts:
                videos.append(file)
                
        # Extract content from markdown
        title = item
        source_url = ""
        collected_at = ""
        description = ""
        
        if md_file:
            try:
                with open(os.path.join(item_path, md_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                frontmatter, body = parse_frontmatter(content)
                
                title = frontmatter.get('title', title)
                source_url = frontmatter.get('source', '')
                collected_at = frontmatter.get('collected_at', '')
                
                clean_body = re.sub(r'!\[\[.*?\]\]', '', body)
                clean_body = re.sub(r'^#\s+.*?\n', '', clean_body)
                clean_body = re.sub(r'## Metadata.*', '', clean_body, flags=re.DOTALL)
                clean_body = clean_body.strip()
                description = clean_body
            except Exception as e:
                print(f"Error reading md file in {item}: {e}")
                
        # Try metadata.json
        uploader = ""
        like_count = None
        repost_count = None
        duration = None
        
        if json_file:
            try:
                with open(os.path.join(item_path, json_file), 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                uploader = meta.get('uploader', '')
                if not source_url:
                    source_url = meta.get('webpage_url', '')
                if not description:
                    description = meta.get('description', '')
                like_count = meta.get('like_count')
                repost_count = meta.get('repost_count')
                duration = meta.get('duration')
            except Exception as e:
                print(f"Error reading json file in {item}: {e}")
                
        # Map media paths, url encoding directories and filenames separately to preserve slashes
        media_items = []
        images.sort()
        videos.sort()
        
        encoded_item = urllib.parse.quote(item)
        for vid in videos:
            media_items.append({
                "type": "video",
                "path": f"{encoded_item}/{urllib.parse.quote(vid)}"
            })
        for img in images:
            media_items.append({
                "type": "image",
                "path": f"{encoded_item}/{urllib.parse.quote(img)}"
            })
            
        data.append({
            "id": item_id,
            "folderName": item,
            "title": title,
            "category": category,
            "date": date_str,
            "sourceUrl": source_url,
            "collectedAt": collected_at,
            "description": description,
            "uploader": uploader,
            "likeCount": like_count,
            "repostCount": repost_count,
            "duration": duration,
            "media": media_items
        })
        
    data.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    return data

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Scanning directory: {current_dir}")
    extracted_data = scan_directory(current_dir)
    
    output_file = os.path.join(current_dir, 'data.js')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated data file. Do not edit manually.\n")
        f.write("window.COLLECTED_DATA = ")
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
        
    print(f"Successfully processed {len(extracted_data)} folders.")
    print(f"Data saved to {output_file}")
