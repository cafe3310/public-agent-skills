#!/usr/bin/env python3
"""
Chat Screenrec Extractor - Batch Frame Extraction and Native OCR Pipeline
Extracts video frames using ffmpeg according to interval in roi_config.json,
saves frames directly into `video-frames/` named `原始名称-mmssSSS.jpg`,
and saves matching OCR text files `原始名称-mmssSSS.txt` alongside each image.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.m4v', '.webm', '.avi', '.mkv'}

def format_mmss_sss(timestamp_sec: float) -> str:
    """Format seconds into mmssSSS (e.g. 93.5s -> 0133500)"""
    total_ms = int(round(timestamp_sec * 1000))
    m = total_ms // 60000
    rem_ms = total_ms % 60000
    s = rem_ms // 1000
    ms = rem_ms % 1000
    return f"{m:02d}{s:02d}{ms:03d}"

def format_time_display(timestamp_sec: float) -> str:
    m = int(timestamp_sec // 60)
    s = int(timestamp_sec % 60)
    ms = int(round((timestamp_sec - int(timestamp_sec)) * 1000))
    return f"{m:02d}:{s:02d}.{ms:03d}"

def bbox_intersects_roi(item_norm_bbox: dict, roi: dict, threshold: float = 0.35) -> bool:
    """
    Check if OCR bounding box intersects with the given ROI region.
    Coordinates are normalized (0..1, top-left origin).
    """
    ix = item_norm_bbox['x']
    iy = item_norm_bbox['y']
    iw = item_norm_bbox['w']
    ih = item_norm_bbox['h']

    rx = roi['x']
    ry = roi['y']
    rw = roi['w']
    rh = roi['h']

    # Compute intersection rectangle
    x_left = max(ix, rx)
    y_top = max(iy, ry)
    x_right = min(ix + iw, rx + rw)
    y_bottom = min(iy + ih, ry + rh)

    if x_right < x_left or y_bottom < y_top:
        return False

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    item_area = max(1e-6, iw * ih)
    return (intersection_area / item_area) >= threshold

def ensure_ocr_binary(script_dir: Path) -> Path:
    """Ensure ocr_vision executable is compiled from Swift"""
    bin_path = script_dir / "ocr_vision"
    swift_path = script_dir / "ocr_vision.swift"

    if bin_path.exists() and os.access(bin_path, os.X_OK):
        return bin_path

    print(f"[*] Compiling native macOS Apple Vision OCR tool ({swift_path.name})...")
    res = subprocess.run(["swiftc", "-O", str(swift_path), "-o", str(bin_path)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error compiling Swift OCR binary:\n{res.stderr}", file=sys.stderr)
        raise RuntimeError("Failed to compile native OCR tool with swiftc")
    print(f"[✓] Native OCR binary compiled successfully: {bin_path}")
    return bin_path

def process_video(video_path: Path, config: dict, script_dir: Path, output_dir: Path, ocr_bin: Path):
    video_stem = video_path.stem
    interval = float(config.get("interval_seconds", 0.8))
    title_roi = config.get("title_roi", {"x": 0.0, "y": 0.04, "w": 1.0, "h": 0.08})
    body_roi = config.get("body_roi", {"x": 0.0, "y": 0.12, "w": 1.0, "h": 0.78})

    # Video frames directory
    video_frames_dir = output_dir / "video-frames"
    video_frames_dir.mkdir(parents=True, exist_ok=True)

    # Temp raw frames directory for ffmpeg extraction
    temp_frames_dir = output_dir / ".cache" / "raw_frames" / video_stem
    temp_frames_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[+] Extracting frames for: {video_path.name} (Sampling interval: {interval}s)")
    
    # Extract frames using ffmpeg
    frame_pattern = str(temp_frames_dir / "temp_%06d.jpg")
    cmd_extract = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"fps=1/{interval}",
        "-q:v", "2",
        frame_pattern
    ]
    subprocess.run(cmd_extract, capture_output=True, check=True)

    raw_frames = sorted(list(temp_frames_dir.glob("temp_*.jpg")))
    print(f"    Extracted {len(raw_frames)} frames.")

    if not raw_frames:
        print(f"[!] No frames extracted for {video_path.name}")
        return []

    # Move/copy frames to video-frames/ with naming format `原始名称-mmssSSS.jpg`
    final_frame_paths = []
    frame_timestamps = {}

    for idx, raw_img in enumerate(raw_frames):
        ts = round(idx * interval, 3)
        code = format_mmss_sss(ts)
        target_name = f"{video_stem}-{code}.jpg"
        target_path = video_frames_dir / target_name
        shutil.copy2(raw_img, target_path)
        final_frame_paths.append(target_path)
        frame_timestamps[str(target_path)] = ts

    # Run native Apple Vision OCR on the target frames
    print(f"[*] Running native Apple Vision OCR on {len(final_frame_paths)} frames in video-frames/...")
    ocr_raw_json_path = output_dir / ".cache" / "ocr_results" / f"{video_stem}_raw_ocr.json"
    ocr_raw_json_path.parent.mkdir(parents=True, exist_ok=True)

    # Pass list of files to ocr_vision
    list_json_path = output_dir / ".cache" / f"{video_stem}_filelist.json"
    with open(list_json_path, "w", encoding="utf-8") as f:
        json.dump([str(p) for p in final_frame_paths], f)

    cmd_ocr = [str(ocr_bin), str(list_json_path), "-o", str(ocr_raw_json_path)]
    subprocess.run(cmd_ocr, check=True)

    with open(ocr_raw_json_path, "r", encoding="utf-8") as f:
        ocr_raw_data = json.load(f)

    # Process each frame, classify items by ROI, and save companion .txt file
    structured_frames = []
    for idx, item in enumerate(ocr_raw_data):
        img_path = Path(item["image_path"])
        ts = frame_timestamps.get(str(img_path), round(idx * interval, 3))
        time_display = format_time_display(ts)

        results = item.get("results", [])
        title_items = []
        body_items = []

        for r in results:
            norm_bbox = r.get("normalized_bbox", {})
            text = r.get("text", "").strip()
            if not text:
                continue

            if bbox_intersects_roi(norm_bbox, title_roi):
                title_items.append(r)
            elif bbox_intersects_roi(norm_bbox, body_roi):
                body_items.append(r)

        # Sort title items by horizontal x coordinate
        title_items.sort(key=lambda x: x["normalized_bbox"]["x"])
        title_text = " ".join([t["text"] for t in title_items]).strip()

        # Sort body items from top to bottom (y coordinate)
        body_items.sort(key=lambda x: x["normalized_bbox"]["y"])

        # Create companion text file: 原始名称-mmssSSS.txt
        txt_path = img_path.with_suffix(".txt")
        txt_lines = []
        txt_lines.append("=" * 72)
        txt_lines.append(f"视频来源 : {video_path.name}")
        txt_lines.append(f"时间戳   : {time_display} (t = {ts:.3f}s)")
        txt_lines.append(f"对应图片 : {img_path.name}")
        txt_lines.append(f"分辨率   : {item.get('width', 0)} x {item.get('height', 0)}")
        txt_lines.append("=" * 72)
        txt_lines.append("")
        txt_lines.append("[群聊标题栏 (Title ROI)]")
        txt_lines.append(title_text if title_text else "(未识别到标题)")
        txt_lines.append("")
        txt_lines.append("[聊天消息区文本 (Body ROI Lines)]")
        txt_lines.append("格式说明: [y坐标 | 区域尺寸 WxH | 估算字号 pt / px] 文本内容")
        txt_lines.append("-" * 72)
        if body_items:
            for b in body_items:
                ny = b["normalized_bbox"]["y"]
                w_px = b.get("width_px", b["bbox"]["w"])
                h_px = b.get("height_px", b["bbox"]["h"])
                f_pt = b.get("font_size_pt", round(h_px / 3.0, 1))
                f_px = b.get("font_size_px", h_px)
                txt_lines.append(f"[y={ny:.3f} | {w_px:.0f}x{h_px:.0f}px | {f_pt:.1f}pt / {f_px:.0f}px] {b['text']}")
        else:
            txt_lines.append("(本帧无消息文本)")
        txt_lines.append("")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(txt_lines))

        structured_frames.append({
            "video_file": video_path.name,
            "frame_index": idx,
            "timestamp": ts,
            "time_display": time_display,
            "image_path": str(img_path),
            "txt_path": str(txt_path),
            "title_text": title_text,
            "title_items": title_items,
            "body_items": body_items,
            "width": item.get("width", 0),
            "height": item.get("height", 0)
        })

    video_structured_path = output_dir / ".cache" / "ocr_results" / f"{video_stem}_structured.json"
    with open(video_structured_path, "w", encoding="utf-8") as f:
        json.dump(structured_frames, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved {len(final_frame_paths)} images & text files in: {video_frames_dir}")
    return structured_frames

def main():
    parser = argparse.ArgumentParser(description="Batch Frame Extraction and Native OCR Pipeline")
    parser.add_argument("--config", "-c", help="Path to roi_config.json")
    parser.add_argument("--video-dir", "-v", default=".", help="Directory containing videos (if config not specified)")
    parser.add_argument("--output-dir", "-o", help="Output directory for frames, txt files and OCR results")
    parser.add_argument("--interval", type=float, default=None, help="Override sampling interval in seconds")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    ocr_bin = ensure_ocr_binary(script_dir)

    video_dir = Path(args.video_dir).resolve()
    config_file = None

    if args.config:
        config_file = Path(args.config).resolve()
        video_dir = config_file.parent
    else:
        candidate_cfg = video_dir / "roi_config.json"
        if candidate_cfg.exists():
            config_file = candidate_cfg

    config = {}
    if config_file and config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"[*] Loaded configuration from: {config_file}")
    else:
        print("[*] No roi_config.json found; using default phone screen presets.")
        config = {
            "interval_seconds": 0.8,
            "title_roi": {"x": 0.0, "y": 0.04, "w": 1.0, "h": 0.08},
            "body_roi": {"x": 0.0, "y": 0.12, "w": 1.0, "h": 0.78}
        }

    if args.interval:
        config["interval_seconds"] = args.interval

    output_dir = Path(args.output_dir).resolve() if args.output_dir else video_dir

    # Find video files
    video_files = []
    for root, _, files in os.walk(video_dir):
        if "/." in root or "\\." in root or "video-frames" in root:
            continue
        for file in sorted(files):
            if Path(file).suffix.lower() in VIDEO_EXTENSIONS:
                video_files.append(Path(root) / file)

    if not video_files:
        print(f"[!] No video files found in {video_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Found {len(video_files)} video files in {video_dir}")
    all_frames_data = []

    for v_path in video_files:
        frames = process_video(v_path, config, script_dir, output_dir, ocr_bin)
        all_frames_data.extend(frames)

    all_data_path = output_dir / ".cache" / "ocr_results" / "all_frames_data.json"
    all_data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(all_data_path, "w", encoding="utf-8") as f:
        json.dump(all_frames_data, f, indent=2, ensure_ascii=False)

    print(f"\n================================================================")
    print(f" Batch OCR Complete!")
    print(f" Frames Directory       : {output_dir / 'video-frames'}")
    print(f" Total frames processed : {len(all_frames_data)}")
    print(f" Consolidated JSON      : {all_data_path}")
    print(f"================================================================")

if __name__ == "__main__":
    main()
