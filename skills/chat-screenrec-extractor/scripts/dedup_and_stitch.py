#!/usr/bin/env python3
"""
Chat Screenrec Extractor - Scroll Deduplication and Message Stitching Engine
Analyzes sequential OCR frames, detects group transitions via Title ROI,
tracks vertical scroll displacements to eliminate duplicate lines, and stitches
messages into coherent chat conversation streams.
Supports forward and reverse (down-scrolling / late-to-early) recordings.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

DATETIME_PATTERNS = [
    r'^(?:昨天|前天|今天|明天|Yesterday|Today)?\s*(?:上午|下午|中午|凌晨|晚上)?\s*\d{1,2}:\d{2}$',
    r'^\d{4}[年\.\-/]\d{1,2}[月\.\-/]\d{1,2}日?(?:\s*(?:上午|下午|中午|凌晨|晚上)?\s*\d{1,2}:\d{2})?$',
    r'^\d{1,2}[月/]\d{1,2}日?(?:\s*(?:上午|下午|中午|凌晨|晚上)?\s*\d{1,2}:\d{2})?$',
    r'^(?:周一|周二|周三|周四|周五|周六|周日|星期[一二三四五六日]|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:\s*(?:上午|下午|中午|凌晨|晚上)?\s*\d{1,2}:\d{2})?$',
    r'^\d{1,2}:\d{2}$',
    r'^ts:\d{4}-\d{2}-\d{2}.*$'
]

SYSTEM_PATTERNS = [
    r'.*加入了群聊.*',
    r'.*移出了群聊.*',
    r'.*退出了群聊.*',
    r'.*撤回了一条消息.*',
    r'.*recalled a message.*',
    r'.*invited.*to the group chat.*',
    r'.*joined the group chat.*',
    r'.*left the group chat.*',
    r'.*拍了拍.*',
    r'.*修改群名为.*',
    r'.*你已添加了.*现在可以开始聊天了.*',
    r'.*开启了群聊邀请确认.*'
]

# Title texts/patterns that indicate main screen or iOS system banners / status bars
IGNORE_TITLE_PATTERNS = [
    r'minimized\s*chats', r'^chats$', r'^wechat$', r'^微信$', r'^通讯录$', r'^发现$', r'^我$',
    r'^search$', r'^搜索$', r'do\s*not\s*disturb', r'turned.*on', r'^focus\b', r'screen\s*recording',
    r'中国联通', r'中国移动', r'中国电信', r'^\%+$', r'^[^\w\u4e00-\u9fa5]+$'
]

def is_ignored_or_system_title(title: str) -> bool:
    t = clean_text(title).lower()
    if not t or t == "未命名群聊" or len(t) <= 1:
        return True
    for pat in IGNORE_TITLE_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False

def clean_text(text: str) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def text_similarity(s1: str, s2: str) -> float:
    """Calculate string similarity ratio"""
    s1 = clean_text(s1)
    s2 = clean_text(s2)
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
    if s1 in s2 or s2 in s1:
        shorter = min(len(s1), len(s2))
        longer = max(len(s1), len(s2))
        if shorter >= 4 and (shorter / longer) > 0.7:
            return 0.95
    return difflib.SequenceMatcher(None, s1, s2).ratio()

def is_datetime_string(text: str) -> bool:
    t = clean_text(text)
    for pat in DATETIME_PATTERNS:
        if re.match(pat, t, re.IGNORECASE):
            return True
    return False

def is_system_notice(text: str) -> bool:
    t = clean_text(text)
    for pat in SYSTEM_PATTERNS:
        if re.match(pat, t, re.IGNORECASE):
            return True
    return False

def normalize_title(title: str) -> str:
    """Extract clean group name from Title ROI text"""
    t = clean_text(title)
    if not t:
        return ""
    # Remove leading status bar / iOS artifacts (e.g. '.12 ', '•1• ', '•ol ', 'Minin面', 'MinimizedChats')
    t = re.sub(r'^(?:[•\.\s\d\-\_\|]+\b|•\w+[\s\d]*|Minin[面\w]*|Minimized\s*Chats[\w\s]*)', '', t, flags=re.IGNORECASE)
    # Remove back arrow prefixes and unread counts like '<35'
    t = re.sub(r'^[<＜〈«\s\d\(\)（）]+', '', t)
    # Remove trailing WeChat icons, dots, audio icons, member indicators (e.g. 込, 公, A••, Q, 以, •⋯••)
    t = re.sub(r'[\s\.\…\—\-\_以込公Q2A•⋯\^]+$', '', t)
    return t.strip()

def cluster_frame_lines(body_items: List[Dict[str, Any]], height: int) -> List[Dict[str, Any]]:
    """
    Sort body items top-to-bottom and merge adjacent fragments that belong to the same line
    """
    if not body_items:
        return []

    # Sort primarily by y coordinate
    sorted_items = sorted(body_items, key=lambda x: (x["normalized_bbox"]["y"], x["normalized_bbox"]["x"]))
    
    merged_lines = []
    current_line = None

    for item in sorted_items:
        norm = item["normalized_bbox"]
        text = clean_text(item["text"])
        if not text:
            continue
        
        # Filter UI artifacts like single random letters or "^ 788 new messages"
        if text.startswith('^') and 'new messages' in text.lower():
            continue

        if current_line is None:
            current_line = {
                "text": text,
                "confidence": item["confidence"],
                "bbox": item["bbox"],
                "normalized_bbox": dict(norm),
                "items": [item]
            }
        else:
            prev_norm = current_line["normalized_bbox"]
            y_diff = abs(norm["y"] - prev_norm["y"])
            line_height = max(prev_norm["h"], norm["h"], 0.015)
            
            if y_diff < (line_height * 0.45):
                # Same line, merge horizontally
                current_line["text"] += " " + text
                current_line["items"].append(item)
                new_right = max(prev_norm["x"] + prev_norm["w"], norm["x"] + norm["w"])
                current_line["normalized_bbox"]["w"] = new_right - prev_norm["x"]
                current_line["normalized_bbox"]["h"] = max(prev_norm["h"], norm["h"])
            else:
                merged_lines.append(current_line)
                current_line = {
                    "text": text,
                    "confidence": item["confidence"],
                    "bbox": item["bbox"],
                    "normalized_bbox": dict(norm),
                    "font_size_pt": item.get("font_size_pt", round(item["bbox"]["h"] / 3.0, 1)),
                    "font_size_px": item.get("font_size_px", item["bbox"]["h"]),
                    "width_px": item.get("width_px", item["bbox"]["w"]),
                    "items": [item]
                }

    if current_line:
        merged_lines.append(current_line)

    return merged_lines

def dedup_session_frames(frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate scrolling lines across successive frames in a single group session.
    """
    emitted_records: List[Dict[str, Any]] = []
    
    for f_idx, frame in enumerate(frames):
        lines = cluster_frame_lines(frame.get("body_items", []), frame.get("height", 2622))
        if not lines:
            continue

        if not emitted_records:
            # First frame: emit all valid lines
            for line in lines:
                emitted_records.append({
                    "text": line["text"],
                    "frame_index": frame["frame_index"],
                    "timestamp": frame["timestamp"],
                    "normalized_bbox": line["normalized_bbox"],
                    "font_size_pt": line.get("font_size_pt", 16.0),
                    "font_size_px": line.get("font_size_px", 48.0),
                    "width_px": line.get("width_px", 200.0),
                    "is_datetime": is_datetime_string(line["text"]),
                    "is_system": is_system_notice(line["text"])
                })
            continue

def find_frame_overlap_index(emitted_tail: List[Dict[str, Any]], frame_lines: List[Dict[str, Any]]) -> int:
    """
    Finds the physical scroll overlap index in frame_lines.
    A valid scrolling overlap must align a prefix near the top of frame_lines (start_f in 0..3)
    with the exact tail of emitted_tail.
    Returns the last overlapping line index in frame_lines (-1 if no overlap).
    """
    if not emitted_tail or not frame_lines:
        return -1

    best_match_idx = -1
    best_score = 0

    for start_f in range(min(4, len(frame_lines))):
        for match_len in range(1, min(len(frame_lines) - start_f + 1, len(emitted_tail) + 1)):
            f_slice = frame_lines[start_f : start_f + match_len]
            e_slice = emitted_tail[-match_len :]

            matched_count = 0
            total_chars = 0
            for f_item, e_item in zip(f_slice, e_slice):
                s = text_similarity(f_item["text"], e_item["text"])
                if s >= 0.70:
                    matched_count += 1
                    total_chars += len(f_item["text"])

            # Valid physical scrolling overlap:
            if (matched_count == match_len or (match_len >= 3 and matched_count >= match_len - 1)) and (matched_count >= 2 or total_chars >= 8):
                end_f = start_f + match_len - 1
                if total_chars > best_score:
                    best_score = total_chars
                    best_match_idx = end_f

    return best_match_idx

def dedup_session_frames(frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate scrolling lines across successive frames in a single group session.
    """
    emitted_records: List[Dict[str, Any]] = []

    for f_idx, frame in enumerate(frames):
        lines = cluster_frame_lines(frame.get("body_items", []), frame.get("height", 2622))
        if not lines:
            continue

        if not emitted_records:
            # First frame: emit all valid lines
            for line in lines:
                emitted_records.append({
                    "text": line["text"],
                    "frame_index": frame["frame_index"],
                    "timestamp": frame["timestamp"],
                    "normalized_bbox": line["normalized_bbox"],
                    "font_size_pt": line.get("font_size_pt", 16.0),
                    "font_size_px": line.get("font_size_px", 48.0),
                    "width_px": line.get("width_px", 200.0),
                    "is_datetime": is_datetime_string(line["text"]),
                    "is_system": is_system_notice(line["text"])
                })
            continue

        # Find prefix-suffix physical scrolling overlap
        last_matched_frame_line_idx = find_frame_overlap_index(emitted_records[-25:], lines)

        new_lines_start = last_matched_frame_line_idx + 1
        for i in range(new_lines_start, len(lines)):
            line = lines[i]
            if emitted_records and text_similarity(line["text"], emitted_records[-1]["text"]) >= 0.85:
                continue

            emitted_records.append({
                "text": line["text"],
                "frame_index": frame["frame_index"],
                "timestamp": frame["timestamp"],
                "normalized_bbox": line["normalized_bbox"],
                "font_size_pt": line.get("font_size_pt", 16.0),
                "font_size_px": line.get("font_size_px", 48.0),
                "width_px": line.get("width_px", 200.0),
                "is_datetime": is_datetime_string(line["text"]),
                "is_system": is_system_notice(line["text"])
            })

    return emitted_records

def assemble_chat_dialogue(emitted_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assemble stream of raw text lines into structured chat dialogue blocks:
    - Dates / time headers
    - System messages
    - User messages with sender and content
    """
    messages = []
    current_msg = None
    current_time_tag = ""

    for rec in emitted_records:
        text = rec["text"].strip()
        if not text:
            continue

        if rec["is_datetime"]:
            if current_msg:
                messages.append(current_msg)
                current_msg = None
            current_time_tag = text
            messages.append({
                "type": "datetime",
                "text": text,
                "video_timestamp": rec["timestamp"]
            })
            continue

        if rec["is_system"]:
            if current_msg:
                messages.append(current_msg)
                current_msg = None
            messages.append({
                "type": "system",
                "text": text,
                "video_timestamp": rec["timestamp"]
            })
            continue

        # Check if text matches "Sender: Content" or "Sender：Content"
        sender_match = re.match(r'^([\u4e00-\u9fa5a-zA-Z0-9_\-\.\s\(\)（）]{1,20})[：:](.+)$', text)
        if sender_match:
            q_sender = sender_match.group(1).strip()
            q_content = sender_match.group(2).strip()

            # Ignore URL protocol prefixes
            if q_sender.lower() in ("http", "https"):
                if current_msg:
                    current_msg["content_lines"].append(text)
                continue

            # If current_msg has content and q_sender is different, this is a Quote Reply (微信引用回复)
            if current_msg and current_msg["content_lines"] and q_sender != current_msg["sender"]:
                current_msg.setdefault("quotes", []).append({
                    "quoted_sender": q_sender,
                    "text": q_content
                })
                continue

            if current_msg and (current_msg["content_lines"] or current_msg["sender"] != "发言人"):
                messages.append(current_msg)
            current_msg = {
                "type": "message",
                "sender": q_sender,
                "time_header": current_time_tag,
                "video_timestamp": rec["timestamp"],
                "content_lines": [q_content] if q_content else [],
                "quotes": []
            }
            continue

        # Check if this line is a standalone sender name tag
        # Characteristics: font size <= 13.5pt (<= 42px), short text, no sentence-ending punctuation
        font_pt = rec.get("font_size_pt", 16.0)
        is_sender_tag = (
            font_pt <= 13.5
            and len(text) <= 18 
            and not any(text.endswith(p) for p in "。？！，,.!?~…、")
            and not re.search(r'^(好的|收到|嗯嗯|对|没有|是的|感谢|抱歉|另外|如果|目前|预计|建议|可以|这个|那|详细|上线|同时|假设|1\.|2\.|3\.|4\.|5\.|@|http)', text)
        )

        if is_sender_tag:
            # If current_msg already has content or is a different sender, flush it
            if current_msg and current_msg["content_lines"]:
                messages.append(current_msg)
            current_msg = {
                "type": "message",
                "sender": text,
                "time_header": current_time_tag,
                "video_timestamp": rec["timestamp"],
                "content_lines": [],
                "quotes": []
            }
        elif current_msg:
            # If current_msg has quotes and line is continuation of quote (font <= 16pt)
            if current_msg.get("quotes") and font_pt <= 16.5:
                current_msg["quotes"][-1]["text"] += " " + text
            # If line is part of a URL (e.g. 'https://' followed by domain), join them
            elif current_msg["content_lines"] and current_msg["content_lines"][-1].startswith("http") and not (" " in current_msg["content_lines"][-1]):
                prev = current_msg["content_lines"][-1]
                if prev.endswith("/") and text.startswith("/"):
                    current_msg["content_lines"][-1] = prev + text[1:]
                else:
                    current_msg["content_lines"][-1] = prev + text
            elif text.startswith("//") and current_msg["content_lines"] and current_msg["content_lines"][-1].startswith("http"):
                current_msg["content_lines"][-1] += text
            else:
                current_msg["content_lines"].append(text)
        else:
            current_msg = {
                "type": "message",
                "sender": "发言人",
                "time_header": current_time_tag,
                "video_timestamp": rec["timestamp"],
                "content_lines": [text],
                "quotes": []
            }

    if current_msg:
        messages.append(current_msg)

    final_messages = []
    for m in messages:
        if m["type"] == "message":
            # Clean up content
            lines = [l.strip() for l in m["content_lines"] if l.strip()]
            content = "\n".join(lines).strip()
            # If content is empty but sender exists and looks like content, adjust
            sender = m["sender"]
            if not content and sender:
                content = sender
                sender = "发言人"
            
            if content:
                final_messages.append({
                    "type": "message",
                    "sender": sender,
                    "time_header": m.get("time_header", ""),
                    "video_timestamp": m.get("video_timestamp", 0.0),
                    "content": content,
                    "quotes": m.get("quotes", [])
                })
        else:
            final_messages.append(m)

    return final_messages

def load_review_mapping(review_file: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Parse user-reviewed title mappings from title_segments_review.md"""
    if not review_file or not review_file.exists():
        return {}

    content = review_file.read_text(encoding="utf-8")
    video_sections = re.split(r"^##\s*📹\s*`([^`]+)`", content, flags=re.MULTILINE)
    mapping = {}

    for i in range(1, len(video_sections), 2):
        v_name = video_sections[i].strip()
        v_body = video_sections[i+1]

        default_target = None
        default_match = re.search(r"^-->\s*([^\n]+)", v_body, flags=re.MULTILINE)
        if default_match:
            default_target = default_match.group(1).strip()

        table_rows = re.findall(r"^\|\s*([0-9\.]+s\s*~\s*[0-9\.]+s)\s*\|\s*(\d+)\.\.(\d+)\s*\([^\)]*\)\s*\|\s*(\d+)\s*\|\s*([^\|]+)\|\s*([^\|]*)\|", v_body, flags=re.MULTILINE)

        seg_list = []
        for r in table_rows:
            time_range, start_f, end_f, cnt, raw_tit, target = r
            start_f = int(start_f)
            end_f = int(end_f)
            target = target.strip()
            if target.startswith("-->"):
                target = target.replace("-->", "").strip()
            elif not target and default_target:
                target = default_target

            seg_list.append({
                "start_frame": start_f,
                "end_frame": end_f,
                "target_group": target if target else None
            })
        mapping[v_name] = seg_list

    return mapping

def process_all_frames_into_groups(
    all_frames: List[Dict[str, Any]], 
    reverse_chronological: bool = True,
    review_mapping: Optional[Dict[str, List[Dict[str, Any]]]] = None
) -> List[Dict[str, Any]]:
    """
    Split all frames across multiple videos by group name, then deduplicate each group.
    If review_mapping is provided, strictly follow user-corrected segment mappings.
    """
    if not all_frames:
        return []

    # If user provided review mappings, use them directly
    if review_mapping:
        group_frames_map: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for f in all_frames:
            v_name = f.get("video_file", "")
            f_idx = f.get("frame_index", 0)
            segs = review_mapping.get(v_name, [])
            target = None
            for s in segs:
                if s["start_frame"] <= f_idx <= s["end_frame"]:
                    target = s["target_group"]
                    break
            
            if target:
                group_frames_map.setdefault(target, {}).setdefault(v_name, []).append(f)

        results = []
        for group_name, v_map in sorted(group_frames_map.items()):
            # Order videos so earliest dates come first
            ordered_v_keys = sorted(v_map.keys(), reverse=True) if reverse_chronological else sorted(v_map.keys())
            combined_frames = []
            source_videos = set()

            for vk in ordered_v_keys:
                frames_in_v = v_map[vk]
                if reverse_chronological:
                    frames_in_v = list(reversed(frames_in_v))
                combined_frames.extend(frames_in_v)
                source_videos.add(vk)

            emitted = dedup_session_frames(combined_frames)
            messages = assemble_chat_dialogue(emitted)
            results.append({
                "group_name": group_name,
                "source_videos": sorted(list(source_videos)),
                "total_frames_inspected": len(combined_frames),
                "messages_count": len(messages),
                "messages": messages
            })
        return results

    # Fallback to automatic heuristic clustering if no review mapping
    videos_map = {}
    for f in all_frames:
        v_file = f.get("video_file", "unknown")
        videos_map.setdefault(v_file, []).append(f)

    ordered_video_keys = sorted(videos_map.keys(), reverse=True) if reverse_chronological else sorted(videos_map.keys())

    ordered_frames = []
    for v_file in ordered_video_keys:
        v_frames = videos_map[v_file]
        filtered = []
        for f in v_frames:
            raw_title = f.get("title_text", "").strip()
            norm_t = normalize_title(raw_title)
            if re.search(r'^(minimized chats|chats|wechat|微信|通讯录|发现|我|search|搜索)$', norm_t, re.IGNORECASE):
                continue
            filtered.append(f)
        if not filtered:
            filtered = v_frames

        if reverse_chronological:
            filtered = list(reversed(filtered))

        ordered_frames.extend(filtered)

    sessions: List[Dict[str, Any]] = []

    for frame in ordered_frames:
        title = normalize_title(frame.get("title_text", ""))
        is_transient = is_ignored_or_system_title(title)

        if not sessions:
            if not is_transient and title:
                sessions.append({
                    "group_name": title,
                    "source_videos": {frame.get("video_file", "")},
                    "frames": [frame]
                })
        else:
            matched_session = None
            last_session = sessions[-1]
            if is_transient or text_similarity(title, last_session["group_name"]) >= 0.55:
                matched_session = last_session
            else:
                for s in sessions:
                    if text_similarity(title, s["group_name"]) >= 0.65:
                        matched_session = s
                        break

            if matched_session:
                matched_session["frames"].append(frame)
                matched_session["source_videos"].add(frame.get("video_file", ""))
            elif not is_transient and title:
                sessions.append({
                    "group_name": title,
                    "source_videos": {frame.get("video_file", "")},
                    "frames": [frame]
                })

    results = []
    for s in sessions:
        emitted = dedup_session_frames(s["frames"])
        messages = assemble_chat_dialogue(emitted)
        results.append({
            "group_name": s["group_name"],
            "source_videos": sorted(list(s["source_videos"])),
            "total_frames_inspected": len(s["frames"]),
            "messages_count": len(messages),
            "messages": messages
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="Scroll Deduplication and Message Stitching Engine")
    parser.add_argument("--ocr-data", "-i", help="Path to all_frames_data.json or directory containing it")
    parser.add_argument("--output-dir", "-o", default="./output", help="Output directory")
    parser.add_argument("--review-file", "-r", help="Path to title_segments_review.md containing user-corrected group names")
    parser.add_argument("--direction", choices=["reverse", "forward"], default="reverse",
                        help="Scrolling direction: 'reverse' for swiping down (late to early), 'forward' for standard")
    args = parser.parse_args()

    input_path = Path(args.ocr_data or "./.cache/ocr_results/all_frames_data.json").resolve()
    if input_path.is_dir():
        candidate = input_path / "all_frames_data.json"
        if candidate.exists():
            input_path = candidate

    if not input_path.exists():
        print(f"[!] OCR data file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Reading OCR data from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        all_frames = json.load(f)

    # Check for title_segments_review.md
    review_path = None
    if args.review_file:
        review_path = Path(args.review_file).resolve()
    else:
        candidate_review = input_path.parent.parent.parent / "title_segments_review.md"
        if candidate_review.exists():
            review_path = candidate_review

    review_mapping = None
    if review_path and review_path.exists():
        print(f"[*] Loading reviewed group title mappings from: {review_path}")
        review_mapping = load_review_mapping(review_path)

    is_reverse = (args.direction == "reverse")
    print(f"[*] Processing {len(all_frames)} frames (Timeline direction: {'从早到晚 (Reverse scrolling)' if is_reverse else '从晚到早 (Forward)'})...")

    grouped_chats = process_all_frames_into_groups(all_frames, reverse_chronological=is_reverse, review_mapping=review_mapping)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_json = output_dir / "intermediate_chats.json"

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(grouped_chats, f, indent=2, ensure_ascii=False)

    print(f"\n================================================================")
    print(f" Deduplication and Stitching Complete!")
    print(f" Distinct Groups Detected : {len(grouped_chats)}")
    for g in grouped_chats:
        print(f"  - {g['group_name']}: {g['messages_count']} messages / entries (from {len(g['source_videos'])} videos)")
    print(f" Intermediate JSON saved to: {out_json}")
    print(f"================================================================")

if __name__ == "__main__":
    main()
