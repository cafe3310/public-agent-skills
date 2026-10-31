#!/usr/bin/env python3
"""
Chat Screenrec Extractor - Markdown Output Formatter
Transforms intermediate chat structures into clean, beautifully formatted Markdown files,
grouped by chat group.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

def sanitize_filename(name: str) -> str:
    """Sanitize group name for safe filesystem filename"""
    s = re.sub(r'[\\/*?:"<>|]', '_', name)
    s = re.sub(r'\s+', '_', s).strip('_.')
    return s if s else "unknown_group"

def format_group_to_markdown(group: dict) -> str:
    group_name = group.get("group_name", "未命名群聊")
    source_videos = group.get("source_videos", [])
    messages = group.get("messages", [])
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    # YAML Frontmatter
    lines.append("---")
    lines.append(f"title: \"群聊记录：{group_name}\"")
    lines.append(f"group_name: \"{group_name}\"")
    lines.append(f"created_at: \"{now_str}\"")
    lines.append("source_videos:")
    for v in source_videos:
        lines.append(f"  - \"{v}\"")
    lines.append(f"total_messages: {len(messages)}")
    lines.append("---")
    lines.append("")

    # Main Title
    lines.append(f"# 群聊记录：{group_name}")
    lines.append("")
    lines.append(f"> 来源录屏：{', '.join([f'`{v}`' for v in source_videos]) if source_videos else '本地录屏'}")
    lines.append(f"> 整理时间：{now_str}")
    lines.append(f"> 消息总计：{len(messages)} 条")
    lines.append("")
    lines.append("---")
    lines.append("")

    current_date_header = None

    for m in messages:
        mtype = m.get("type", "message")
        
        if mtype == "datetime":
            dt_text = m.get("text", "").strip()
            if dt_text != current_date_header:
                current_date_header = dt_text
                lines.append(f"### 📅 {dt_text}")
                lines.append("")
        elif mtype == "system":
            sys_text = m.get("text", "").strip()
            # Remove redundant '系统提示' prefix if already present in OCR text
            sys_text = re.sub(r'^(?:系统提示|系统消息)[：:\s]*', '', sys_text).strip()
            lines.append("> [!NOTE]")
            lines.append(f"> 系统提示：{sys_text}")
            lines.append("")
        elif mtype == "message":
            sender = m.get("sender", "发言人").strip()
            time_h = m.get("time_header", "").strip()
            content = m.get("content", "").strip()
            quotes = m.get("quotes", [])

            # Extract HH:MM if time_h contains full date
            short_time = ""
            if time_h:
                t_match = re.search(r'(\d{1,2}:\d{2})', time_h)
                short_time = t_match.group(1) if t_match else time_h

            time_prefix = f"[{short_time}] " if short_time else ""
            lines.append(f"**{time_prefix}{sender}**")
            # Preserve multiline content with clean indentation or paragraphs
            content_formatted = "\n".join([f"{line}" for line in content.split("\n") if line.strip()])
            lines.append(content_formatted if content_formatted else "*(空消息)*")
            
            # Render quote replies
            for q in quotes:
                q_author = q.get("quoted_sender", "").strip()
                q_txt = q.get("text", "").strip()
                if q_txt:
                    lines.append(f"> 引用 @{q_author}：{q_txt}")
            lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Format intermediate chat data into grouped Markdown files")
    parser.add_argument("--input", "-i", default="./output/intermediate_chats.json", help="Path to intermediate_chats.json")
    parser.add_argument("--output-dir", "-o", default="./output", help="Directory to save markdown files")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"[!] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        grouped_chats = json.load(f)

    print(f"[*] Formatting {len(grouped_chats)} groups into Markdown...")

    summary_lines = [
        "# 群聊记录汇总索引 (Chat Logs Index)",
        "",
        f"> 生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| 群聊名称 | 消息条数 | 来源视频 | 导出文档 |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for group in grouped_chats:
        gname = group.get("group_name", "未命名群聊")
        md_content = format_group_to_markdown(group)
        safe_name = sanitize_filename(gname)
        out_file = output_dir / f"{safe_name}.md"

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"  [✓] Exported: {out_file.name} ({group.get('messages_count', 0)} msgs)")
        summary_lines.append(
            f"| **{gname}** | {group.get('messages_count', 0)} | {', '.join(group.get('source_videos', []))} | [{safe_name}.md](./{safe_name}.md) |"
        )

    # Save summary index
    summary_path = output_dir / "README.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print(f"\n================================================================")
    print(f" Markdown Generation Complete!")
    print(f" Output directory : {output_dir}")
    print(f" Index file       : {summary_path}")
    print(f"================================================================")

if __name__ == "__main__":
    main()
