import os
import re
import datetime
import argparse
import yaml
import subprocess
import json
import urllib.request

def get_site_type(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    if 'x.com' in url or 'twitter.com' in url:
        return 'x'
    return 'unknown'

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def download_file(url, target_path):
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, target_path)
        return True
    except Exception as e:
        print(f"  [Error] 下载附件失败 {url}: {str(e)}")
        return False

def process_downloads(args):
    list_file = args.list_file
    archive_root = args.archive_dir
    
    if not os.path.exists(list_file):
        print(f"错误：找不到下载列表文件 {list_file}")
        return

    with open(list_file, 'r', encoding='utf-8') as f:
        content = f.read()

    yaml_match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    if not yaml_match:
        print("错误：未在列表中发现 YAML 数据块。")
        return

    try:
        items = yaml.safe_load(yaml_match.group(1))
    except Exception as e:
        print(f"解析 YAML 失败: {str(e)}")
        return

    if not items:
        print("列表为空。")
        return

    now_timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H')

    for item in items:
        if item.get('status') != "待处理":
            continue
            
        url = item.get('url')
        site_type = get_site_type(url)
        tag_type = item.get('tag_type', '#Marker-待下载')
        
        category = "其他"
        cat_match = re.search(r'#Marker-待下载-(.*)', tag_type)
        if cat_match:
            category = cat_match.group(1)

        print(f"\n--- 正在处理 ({site_type}): {url} ---")
        
        if site_type == 'unknown':
            item['status'] = "下载失败（未识别站点）"
            continue

        url_slug = sanitize_filename(url.split('/')[-1].split('?')[0])
        folder_name = f"[{now_timestamp}] {category} {url_slug}"
        target_dir = os.path.join(archive_root, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        success = False
        try:
            # 1. First, get metadata JSON via yt-dlp
            json_cmd = [
                'yt-dlp',
                '--write-info-json',
                '--skip-download',
                '--ignore-no-formats-error',
                '--no-playlist',
                '-o', os.path.join(target_dir, "metadata"),
                url
            ]
            subprocess.run(json_cmd, capture_output=True)
            
            # 2. Try to download video via yt-dlp
            video_cmd = [
                'yt-dlp',
                '--no-playlist',
                '-f', 'bestvideo+bestaudio/best',
                '-o', os.path.join(target_dir, "%(title)s.%(ext)s"),
                url
            ]
            video_result = subprocess.run(video_cmd, capture_output=True, text=True)
            
            # 3. If it's X (Twitter), use gallery-dl to ensure images are captured
            if site_type == 'x':
                print("  正在调用 gallery-dl 抓取多媒体素材...")
                # Force download into the current target_dir
                gdl_cmd = [
                    'gallery-dl',
                    '-D', target_dir,
                    url
                ]
                subprocess.run(gdl_cmd, capture_output=True)

            # 4. Gather all assets and build Markdown
            json_files = [f for f in os.listdir(target_dir) if f.endswith('.json')]
            if json_files:
                json_path = os.path.join(target_dir, json_files[0])
                with open(json_path, 'r', encoding='utf-8') as jf:
                    meta = json.load(jf)
                
                title = meta.get('title', url_slug)
                description = meta.get('description', '')
                
                # Scan for media files
                video_exts = ('.mp4', '.mkv', '.webm', '.mov')
                img_exts = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
                
                all_files = os.listdir(target_dir)
                video_files = [f for f in all_files if f.lower().endswith(video_exts) and not f.endswith('.part')]
                image_files = [f for f in all_files if f.lower().endswith(img_exts)]
                
                # Sort images to keep them in order if possible
                image_files.sort()

                md_filename = f"{folder_name}.md"
                with open(os.path.join(target_dir, md_filename), 'w', encoding='utf-8') as mf:
                    mf.write(f"---\nsource: {url}\ncollected_at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\ntitle: {title}\n---\n\n")
                    mf.write(f"# {title}\n\n")
                    
                    if video_files:
                        mf.write(f"### Video\n![[{video_files[0]}]]\n\n")
                    
                    if image_files:
                        mf.write(f"### Media\n")
                        for img in image_files:
                            mf.write(f"![[{img}]]\n")
                        mf.write("\n")
                    
                    mf.write(f"## Metadata\n\n")
                    mf.write(f"**Original URL**: {url}\n")
                    mf.write(f"**Description**:\n\n{description}\n")
                
                success = True
            else:
                print(f"  [Fail] 无法获取元数据 JSON。")
                success = False
                
        except Exception as e:
            print(f"  [Error] 异常: {str(e)}")
            success = False

        if success:
            item['status'] = "下载完成"
            item['archive_link'] = f"[[{os.path.join(folder_name, folder_name + '.md')}]]"
        else:
            item['status'] = "下载失败"

    new_yaml = yaml.dump(items, allow_unicode=True, sort_keys=False)
    new_content = re.sub(r'```yaml\n.*?\n```', f"```yaml\n{new_yaml}```", content, flags=re.DOTALL)
    
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("\n任务处理完成。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="执行下载列表中的剪藏任务")
    parser.add_argument("--list-file", required=True, help="待处理的下载列表 .md 文件路径")
    parser.add_argument("--archive-dir", required=True, help="剪藏内容存储的全路径")
    
    args = parser.parse_args()
    process_downloads(args)
