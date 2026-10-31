import os
import json
import re
import base64
import urllib.parse
import subprocess
import tempfile
from io import BytesIO
from PIL import Image

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

def compress_pil_image_to_base64(img, max_size=400, quality=45):
    """
    Compress a PIL Image object to WebP and return base64 encoded data URI.
    """
    try:
        # Handle color mode compatibility (convert RGBA/LA/P to RGBA/RGB)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        
        # Scale image down if it exceeds maximum allowed dimension
        w, h = img.size
        if w > max_size or h > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save into memory buffer as WEBP
        output = BytesIO()
        img.save(output, format="WEBP", quality=quality)
        webp_bytes = output.getvalue()
        
        # Base64 Encode
        base64_str = base64.b64encode(webp_bytes).decode('utf-8')
        return f"data:image/webp;base64,{base64_str}"
    except Exception as e:
        print(f"Error compressing PIL image: {e}")
        return None

def compress_image_to_base64(img_path, max_size=400, quality=45):
    """
    Open an image, resize it if it exceeds max_size, convert it to WebP,
    and return the base64 encoded data URI.
    """
    try:
        if not os.path.exists(img_path):
            print(f"Warning: Image file not found: {img_path}")
            return None
            
        with Image.open(img_path) as img:
            return compress_pil_image_to_base64(img, max_size=max_size, quality=quality)
    except Exception as e:
        print(f"Error compressing image {img_path}: {e}")
        return None

def extract_video_thumb(video_path):
    """
    Extract the first frame from a video using ffmpeg and return as PIL.Image.
    """
    if not os.path.exists(video_path):
        return None
        
    temp_dir = tempfile.gettempdir()
    temp_img_path = os.path.join(temp_dir, f"thumb_{os.path.basename(video_path)}.jpg")
    
    if os.path.exists(temp_img_path):
        try:
            os.remove(temp_img_path)
        except Exception:
            pass
            
    try:
        # ffmpeg command to extract the very first frame
        cmd = [
            'ffmpeg', '-y',
            '-ss', '00:00:00',
            '-i', video_path,
            '-vframes', '1',
            '-f', 'image2',
            '-q:v', '2',
            temp_img_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0 and os.path.exists(temp_img_path):
            img = Image.open(temp_img_path)
            img.load()
            return img
    except Exception as e:
        print(f"Error extracting thumb from {video_path}: {e}")
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except Exception:
                pass
    return None

def scan_and_compile_data(base_dir, max_size=400, quality=45):
    data = []
    
    # Supported media types
    img_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
    vid_exts = {'.mp4', '.mov', '.webm', '.m4v'}
    
    # Scan subdirectories
    items = sorted(os.listdir(base_dir))
    total_items = len([it for it in items if os.path.isdir(os.path.join(base_dir, it))])
    processed_count = 0
    
    print(f"Starting compilation. Total directories to scan: {total_items}")
    
    for item in items:
        item_path = os.path.join(base_dir, item)
        if not os.path.isdir(item_path):
            continue
            
        processed_count += 1
        print(f"[{processed_count}/{total_items}] Processing folder: {item}")
        
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
        tags = set()
        
        if md_file:
            try:
                with open(os.path.join(item_path, md_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                frontmatter, body = parse_frontmatter(content)
                
                title = frontmatter.get('title', title)
                source_url = frontmatter.get('source', '')
                collected_at = frontmatter.get('collected_at', '')
                
                # Extract frontmatter tags
                fm_tags = frontmatter.get('tags', '') or frontmatter.get('tag', '')
                if fm_tags:
                    if str(fm_tags).startswith('[') and str(fm_tags).endswith(']'):
                        fm_tags = str(fm_tags)[1:-1]
                    parts = re.split(r'[\s,]+', str(fm_tags))
                    for p in parts:
                        p = p.strip().lstrip('#')
                        if p:
                            tags.add(p)
                            
                # Extract description: try **Description**: block first, fallback to raw text cleaning
                desc_match = re.search(r'\*\*Description\*\*:\s*(.*)', body, re.DOTALL)
                if not desc_match:
                    desc_match = re.search(r'Description:\s*(.*)', body, re.DOTALL)
                    
                if desc_match:
                    desc_text = desc_match.group(1).strip()
                    desc_text = re.sub(r'!\[\[.*?\]\]', '', desc_text)
                    description = desc_text
                else:
                    clean_body = re.sub(r'## Metadata.*', '', body, flags=re.DOTALL)
                    clean_body = re.sub(r'!\[\[.*?\]\]', '', clean_body)
                    clean_body = re.sub(r'^#\s+.*?\n', '', clean_body)
                    clean_body = re.sub(r'### Media.*', '', clean_body, flags=re.DOTALL)
                    description = clean_body.strip()
                
                # Extract Obsidian tags from body (#tag-name)
                if body:
                    body_tags = re.findall(r'(?<!\S)#([\w\u4e00-\u9fa5_-]+)', body)
                    for bt in body_tags:
                        if bt and not re.match(r'^[0-9a-fA-F]{3,6}$', bt):
                            tags.add(bt)
            except Exception as e:
                print(f"Error reading md file in {item}: {e}")
                
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
                json_desc = meta.get('description', '')
                if json_desc and (not description or len(description) < 3):
                    description = json_desc
                like_count = meta.get('like_count')
                repost_count = meta.get('repost_count')
                duration = meta.get('duration')
            except Exception as e:
                print(f"Error reading json file in {item}: {e}")
                
        # Process and compress media items
        media_items = []
        images.sort()
        videos.sort()
        
        # Videos in single page mode do not have paths to prevent external/local links
        for vid in videos:
            media_items.append({
                "type": "video",
                "path": ""
            })
            
        # Images are compressed and inlined as Base64
        for img in images:
            img_path = os.path.join(item_path, img)
            base64_data = compress_image_to_base64(img_path, max_size=max_size, quality=quality)
            if base64_data:
                media_items.append({
                    "type": "image",
                    "path": base64_data
                })
            else:
                # Fallback to relative path if compression fails
                media_items.append({
                    "type": "image",
                    "path": f"{encoded_item}/{urllib.parse.quote(img)}"
                })
                
        # If there are videos but NO images, extract a thumb frame from the first video
        if videos and not images:
            first_vid_path = os.path.join(item_path, videos[0])
            print(f"Extracting thumb for video: {videos[0]}")
            thumb_img = extract_video_thumb(first_vid_path)
            if thumb_img:
                base64_thumb = compress_pil_image_to_base64(thumb_img, max_size=max_size, quality=quality)
                if base64_thumb:
                    media_items.append({
                        "type": "image",
                        "path": base64_thumb
                    })
                
        # Reclassify category based on media contents (文字, 图片, 视频)
        has_video = any(m["type"] == "video" for m in media_items)
        has_image = any(m["type"] == "image" for m in media_items)
        
        if has_video:
            category = "视频"
        elif has_image:
            category = "图片"
        else:
            category = "文字"
            
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
            "media": media_items,
            "tags": sorted(list(tags))
        })
        
    # Sort data by date descending
    data.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    return data

def build_single_page(base_dir, max_size=400, quality=45):
    # 1. Scan directories and compress images to get JSON data
    collected_data = scan_and_compile_data(base_dir, max_size=max_size, quality=quality)
    
    # 2. Read index.html template
    index_path = os.path.join(base_dir, 'index.html')
    if not os.path.exists(index_path):
        print(f"Error: index.html template not found at {index_path}")
        return
        
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # 3. Inline style.css
    css_path = os.path.join(base_dir, 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        # Replace stylesheet link with style tag
        html_content = re.sub(
            r'<link\s+rel=["\']stylesheet["\']\s+href=["\']style\.css["\']\s*\/?>',
            lambda m: f"<style>\n{css_content}\n</style>",
            html_content
        )
    else:
        print("Warning: style.css not found, skipping stylesheet inlining.")
        
    # 4. Read app.js
    app_path = os.path.join(base_dir, 'app.js')
    if os.path.exists(app_path):
        with open(app_path, 'r', encoding='utf-8') as f:
            app_content = f.read()
    else:
        print("Error: app.js not found.")
        return
        
    # 5. Replace external script imports with internal scripts (data.js and app.js)
    # Find scripts section and replace it
    data_json_str = json.dumps(collected_data, ensure_ascii=False, indent=2)
    inlined_scripts = f"""<script>
    // Auto-inlined data. Do not edit.
    window.IS_SINGLE_PAGE = true;
    window.COLLECTED_DATA = {data_json_str};
  </script>
  <script>
    {app_content}
  </script>"""

    # Look for both external scripts and replace them
    pattern = r'<script\s+src=["\']data\.js["\']\s*><\/script>\s*<script\s+src=["\']app\.js["\']\s*><\/script>'
    if re.search(pattern, html_content):
        html_content = re.sub(pattern, lambda m: inlined_scripts, html_content)
    else:
        # Fallback regex matches
        html_content = re.sub(r'<script\s+src=["\']data\.js["\']\s*><\/script>', '', html_content)
        html_content = re.sub(r'<script\s+src=["\']app\.js["\']\s*><\/script>', lambda m: inlined_scripts, html_content)
        
    # 6. Save final HTML file
    output_path = os.path.join(base_dir, 'index_single.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"\nSuccessfully generated Single-Page Gallery HTML: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    build_single_page(current_dir, max_size=400, quality=45)
