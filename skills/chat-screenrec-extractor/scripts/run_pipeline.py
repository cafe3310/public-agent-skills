#!/usr/bin/env python3
"""
Chat Screenrec Extractor - One-click Master Pipeline Runner
Orchestrates the entire flow:
1. Directory inspection & video file listing with interactive confirmation
2. Frame extraction & Apple Vision OCR across all detected videos
3. Scroll deduplication & message stitching
4. Formatted Markdown export
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.webm', '.avi', '.mkv'}

def format_duration(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def get_video_info(video_path: Path) -> dict:
    size_mb = video_path.stat().st_size / (1024 * 1024)
    duration_str = "--:--"
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        dur = float(data.get("format", {}).get("duration", 0.0))
        if dur > 0:
            duration_str = format_duration(dur)
    except Exception:
        pass
    return {
        "path": video_path,
        "name": video_path.name,
        "size_mb": size_mb,
        "duration": duration_str
    }

def scan_videos(video_dir: Path) -> list:
    videos = []
    for root, _, files in os.walk(video_dir):
        if "/." in root or "\\." in root:
            continue
        for file in sorted(files):
            if Path(file).suffix.lower() in VIDEO_EXTENSIONS:
                v_path = Path(root) / file
                videos.append(get_video_info(v_path))
    # Sort naturally by filename
    videos.sort(key=lambda v: v["name"])
    return videos

def run_cmd(cmd, description):
    print(f"\n========================================================", flush=True)
    print(f"▶ Step: {description}", flush=True)
    print(f"  Command: {' '.join(str(c) for c in cmd)}", flush=True)
    print(f"========================================================", flush=True)
    sys.stdout.flush()
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[!] Step failed with return code {res.returncode}", file=sys.stderr, flush=True)
        sys.exit(res.returncode)

def main():
    parser = argparse.ArgumentParser(description="One-click Chat Screenrec Extractor Pipeline")
    parser.add_argument("--video-dir", "-v", default=None, help="Directory containing screen recording videos")
    parser.add_argument("--config", "-c", help="Path to roi_config.json (optional, auto-searches video-dir)")
    parser.add_argument("--output-dir", "-o", help="Output directory for markdown files (default: <video-dir>/output)")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm and bypass interactive prompts")
    parser.add_argument("--skip-extract", action="store_true", help="Skip frame extraction and OCR, re-run deduplication only")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()

    # 1. Resolve video directory
    if args.video_dir:
        video_dir = Path(args.video_dir).resolve()
    else:
        # Prompt interactively if not provided
        print("💬 [Chat Screenrec Extractor]")
        entered = input("请输入包含录屏视频的目录路径 (默认当前目录 .): ").strip()
        video_dir = Path(entered if entered else ".").resolve()

    if not video_dir.exists() or not video_dir.is_dir():
        print(f"[!] 错误: 目录不存在或不是有效目录: {video_dir}", file=sys.stderr)
        sys.exit(1)

    # 2. Scan and list video files
    video_list = scan_videos(video_dir)

    print("\n" + "=" * 62)
    print(f"📁 目标目录: {video_dir}")
    if not video_list:
        print("❌ 未在指定目录下发现任何支持的录屏视频文件 (.mp4, .mov, etc.)")
        print("=" * 62 + "\n")
        sys.exit(1)

    print(f"🎬 共扫描到 {len(video_list)} 个录屏视频文件：")
    print("-" * 62)
    for idx, v in enumerate(video_list, start=1):
        rel_path = v["path"].relative_to(video_dir)
        print(f"  [{idx}] {rel_path}  ({v['size_mb']:.1f} MB | 时长: {v['duration']})")
    print("=" * 62)

    # 3. Interactive confirmation
    if not args.yes:
        try:
            confirm = input(f"\n确认开始批量处理以上 {len(video_list)} 个视频？[Y/n]: ").strip().lower()
            if confirm and confirm != 'y' and confirm != 'yes':
                print("[-] 用户已取消执行。")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("\n[-] 已取消。")
            sys.exit(0)

    config_path = Path(args.config).resolve() if args.config else (video_dir / "roi_config.json")
    output_dir = Path(args.output_dir).resolve() if args.output_dir else (video_dir / "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not config_path.exists() and not args.skip_extract:
        print(f"\n[!] 提示: 未在目录中找到标定配置文件 (roi_config.json)。")
        print(f"    如需精确框选标题与正文区域，可随时在另一终端启动 Web 标定工具:")
        print(f"    python3 {script_dir}/server.py --input-dir {video_dir} --port 8765")
        print(f"    当前将按手机标准全屏预设参数继续运行...\n")

    # Step 1: Batch Frame Extraction & OCR across all videos
    if not args.skip_extract:
        ocr_cmd = [
            sys.executable, str(script_dir / "extract_and_ocr.py"),
            "--video-dir", str(video_dir),
            "--output-dir", str(video_dir)
        ]
        if config_path.exists():
            ocr_cmd.extend(["--config", str(config_path)])
        run_cmd(ocr_cmd, f"Batch Extraction & OCR on {len(video_list)} Videos")

    # Step 2: Deduplication and Stitching across all frames
    all_data_json = video_dir / ".cache" / "ocr_results" / "all_frames_data.json"
    dedup_cmd = [
        sys.executable, str(script_dir / "dedup_and_stitch.py"),
        "--ocr-data", str(all_data_json),
        "--output-dir", str(output_dir)
    ]
    run_cmd(dedup_cmd, "Multi-Video Scroll Deduplication & Message Stitching")

    # Step 3: Markdown Formatting
    intermediate_json = output_dir / "intermediate_chats.json"
    fmt_cmd = [
        sys.executable, str(script_dir / "format_markdown.py"),
        "--input", str(intermediate_json),
        "--output-dir", str(output_dir)
    ]
    run_cmd(fmt_cmd, "Export Consolidated Group Markdown Documents")

    print(f"\n🎉 全部视频处理完毕！Markdown 聊天记录已输出至:\n   👉 {output_dir}\n")

if __name__ == "__main__":
    main()
