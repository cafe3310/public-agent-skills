#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Parse Claude Code session JSONL logs for handoff.")
    parser.add_argument("-f", "--file", required=True, help="Path to a specific session JSONL file, or a Claude Code session ID.")
    parser.add_argument("-p", "--project", help="Path to the project workspace directory (default: current directory).")
    parser.add_argument("-o", "--out", help="Path to write/update HANDOFF.md (default: project_root/HANDOFF.md).")
    parser.add_argument("-n", "--rounds", type=int, default=5, help="Number of dialogue rounds to print in history (default: 5).")
    return parser.parse_args()

def find_session_by_id_or_name(session_ref):
    # Candidate base directories (including standard Claude and Codefuse engine paths)
    base_dirs = [
        os.path.expanduser("~/.claude/projects"),
        os.path.expanduser("~/.codefuse/engine/cc/projects")
    ]
    
    possible_names = [session_ref]
    if not session_ref.endswith(".jsonl"):
        possible_names.append(f"{session_ref}.jsonl")
        
    found_files = []
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file in possible_names or session_ref in file:
                    found_files.append(os.path.join(root, file))
                    
    if found_files:
        # Sort by modification time descending to pick the newest one
        found_files.sort(key=os.path.getmtime, reverse=True)
        return found_files[0], None
        
    return None, f"Could not find any session file matching '{session_ref}' in Claude Code directories."

def format_timestamp(ts_str):
    if not ts_str:
        return "N/A"
    try:
        # e.g., 2026-06-01T17:29:47.416Z -> YYYY-MM-DD HH:mm:ss
        dt = datetime.strptime(ts_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str

def parse_session_file(file_path):
    events = []
    if not os.path.exists(file_path):
        return None, f"File not found: {file_path}"
        
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                events.append(data)
            except Exception as e:
                # Silently skip malformed lines but could report
                pass
    return events, None

def analyze_session(events):
    analysis = {
        "session_id": None,
        "interruption_reason": "Normal termination or user stopped",
        "has_error": False,
        "error_details": None,
        "git_branch": "unknown",
        "cwd": "unknown",
        "latest_handoff_content": None,
        "dialogue": [],
        "last_prompt": None
    }
    
    # Simple values from first events
    for ev in events:
        if "sessionId" in ev and not analysis["session_id"]:
            analysis["session_id"] = ev["sessionId"]
        if "gitBranch" in ev and ev["gitBranch"]:
            analysis["git_branch"] = ev["gitBranch"]
        if "cwd" in ev and ev["cwd"]:
            analysis["cwd"] = ev["cwd"]
            
    # Trace backwards to find API errors, rate limits, or context window exceeded
    for ev in reversed(events):
        t = ev.get("type")
        subtype = ev.get("subtype")
        
        # Check system errors
        if t == "system" and subtype == "api_error":
            error_data = ev.get("error", {})
            analysis["has_error"] = True
            analysis["error_details"] = error_data
            
            status = error_data.get("status")
            formatted = error_data.get("formatted", "")
            msg = error_data.get("message", "")
            
            if status == 429 or "rate_limit" in msg or "额度" in formatted:
                analysis["interruption_reason"] = f"API Rate Limit Exceeded (HTTP 429): {formatted or msg}"
            elif status == 422 or "context_window" in msg or "tokens" in msg:
                analysis["interruption_reason"] = f"Context Window Exceeded (HTTP 422): {formatted or msg}"
            else:
                analysis["interruption_reason"] = f"API Error ({status}): {formatted or msg}"
            break
            
        # Check assistant errors
        elif t == "assistant":
            # Check if it contains an API error inside a text response first for better details
            msg = ev.get("message", {})
            content = msg.get("content")
            content_text = ""
            if isinstance(content, list):
                content_text = "".join([p.get("text", "") for p in content if p.get("type") == "text"])
            else:
                content_text = str(content or "")
                
            if "API Error:" in content_text or "rate_limit" in content_text.lower() or "limit exceeded" in content_text.lower():
                analysis["has_error"] = True
                analysis["error_details"] = content_text
                analysis["interruption_reason"] = content_text.strip().split("\n")[0]
                break

            err_data = ev.get("error")
            if err_data:
                analysis["has_error"] = True
                analysis["error_details"] = err_data
                analysis["interruption_reason"] = f"Assistant execution error: {err_data}"
                break

    # Look for last handoff file in attachments
    for ev in reversed(events):
        t = ev.get("type")
        if t == "attachment":
            att = ev.get("attachment", {})
            if att.get("type") == "file" and "HANDOFF.md" in (att.get("displayPath") or att.get("filename") or ""):
                content = att.get("content", {})
                if isinstance(content, dict):
                    file_data = content.get("file", {})
                    txt = file_data.get("content", "")
                    if txt:
                        analysis["latest_handoff_content"] = txt
                        break

    # Extract dialogues and genuine work history
    dialogue_rounds = []
    genuine_work = []
    
    for ev in events:
        t = ev.get("type")
        ts = format_timestamp(ev.get("timestamp"))
        
        if t == "user":
            msg = ev.get("message", {})
            content = msg.get("content")
            content_text = ""
            
            if isinstance(content, list):
                pieces = []
                for p in content:
                    if p.get("type") == "text":
                        pieces.append(p.get("text", ""))
                content_text = "".join(pieces)
            else:
                content_text = str(content or "")
                
            # If tool use result is embedded
            tool_result = ev.get("toolUseResult")
            if tool_result:
                content_text += f"\n\n[Tool Result]: {str(tool_result)[:300]}..."
                
            current_round = {
                "timestamp": ts,
                "role": "User",
                "content": content_text
            }
            dialogue_rounds.append(current_round)
            
            # Check if genuine work (exclude local commands caveats, handoff trigger prompts, and model config prompts)
            is_env_cmd = any(k in content_text for k in ["local-command-caveat", "command-name", "command-message"])
            is_handoff_hint = "Base directory for this skill" in content_text or "编写或更新交接文档" in content_text
            is_model_hint = "Opus 4.6" in content_text or "Continue from where you left off" in content_text
            
            if not (is_env_cmd or is_handoff_hint or is_model_hint) and len(content_text.strip()) > 5:
                genuine_work.append({
                    "role": "User",
                    "timestamp": ts,
                    "content": content_text.strip(),
                    "tools": []
                })
            
        elif t == "assistant":
            msg = ev.get("message", {})
            content = msg.get("content")
            content_text = ""
            tools = []
            
            if isinstance(content, list):
                pieces = []
                for p in content:
                    if p.get("type") == "text":
                        pieces.append(p.get("text", ""))
                    elif p.get("type") == "tool_use":
                        name = p.get("name")
                        inp = p.get("input", {})
                        pieces.append(f"\n*   **[Tool Call]** `{name}` with args: `{json.dumps(inp, ensure_ascii=False)}`")
                        
                        # Format tools for summary
                        if name in ("WriteToFile", "write_file", "Write"):
                            tools.append(f"Write {inp.get('file_path') or inp.get('path') or inp.get('TargetFile')}")
                        elif name in ("Replace", "replace_file_content", "Edit"):
                            tools.append(f"Edit {inp.get('file_path') or inp.get('path') or inp.get('TargetFile')}")
                        elif name in ("Bash", "run_command"):
                            tools.append(f"Cmd: {inp.get('command') or inp.get('CommandLine')}")
                        else:
                            tools.append(f"{name}({list(inp.keys())})")
                content_text = "".join(pieces)
            else:
                content_text = str(content or "")
                
            current_round = {
                "timestamp": ts,
                "role": "Claude",
                "content": content_text
            }
            dialogue_rounds.append(current_round)
            
            # Exclude error logs / empty notes
            is_err = any(k in content_text for k in ["API Error:", "Rate Limit", "limit exceeded"])
            is_empty_res = "No response requested" in content_text
            
            if not (is_err or is_empty_res) and (tools or len(content_text.strip()) > 10):
                genuine_work.append({
                    "role": "Claude",
                    "timestamp": ts,
                    "content": content_text.strip(),
                    "tools": tools
                })
            
        elif t == "last-prompt":
            analysis["last_prompt"] = ev.get("lastPrompt")

    analysis["dialogue"] = dialogue_rounds
    analysis["genuine_work"] = genuine_work
    return analysis

def build_fallback_handoff(analysis):
    # If no HANDOFF.md was parsed, we synthesize one
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_user_msg = "Unknown"
    for r in reversed(analysis["dialogue"]):
        if r["role"] == "User":
            txt = r["content"].strip()
            if "local-command" not in txt and len(txt) > 2:
                last_user_msg = txt.split("\n")[0]
                break
            
    content = f"""# HANDOFF (Synthesized from Claude Code Session)

*   **生成时间 (Generated)**: {timestamp_str}
*   **原始会话 (Session ID)**: `{analysis['session_id'] or 'N/A'}`
*   **Git 分支 (Branch)**: `{analysis['git_branch']}`
*   **运行目录 (CWD)**: `{analysis['cwd']}`

## 1. 目标 (Objectives)
*   从 Claude Code 会话中断处接续。
*   中断前收到的最后有效指令："{last_user_msg}"

## 2. 当前进展 (Current Progress)
*   Claude Code 会话因为以下原因停下：`{analysis['interruption_reason']}`.

## 3. 中断前的实质性业务动作 (Actionable History)
下面记录了中断前最后几步模型实际执行的文件修改或命令（供接手机制精确参考）：
"""
    # Append recent 8 work events
    recent_work = analysis.get("genuine_work", [])[-8:]
    if recent_work:
        for w in recent_work:
            content += f"\n*   **[{w['timestamp']}] {w['role']}**:\n"
            if w['tools']:
                for t in w['tools']:
                    content += f"    - **调用工具**: `{t}`\n"
            snippet = w['content'].replace('\n', ' ')
            content += f"    - **摘要/描述**: {snippet[:150]}...\n"
    else:
        content += "\n*   *(未检测到相关的实质性文件操作。)*\n"

    content += """
## 4. 后续步骤 (Next Steps)
1. 检查并确认本地 Git 状态是否干净。
2. 核对上述 **“中断前的实质性业务动作”** 涉及的文件改动，定位 Claude 离开时的具体断点。
3. 检查最近运行失败的命令并接续执行任务。
"""
    return content

def main():
    args = parse_args()
    
    project_path = args.project or os.getcwd()
    file_path = args.file
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        print(f"[*] Parsing specified session file: {file_path}")
    else:
        detected_file, err = find_session_by_id_or_name(file_path)
        if err:
            print(f"Error: Provided path '{file_path}' does not exist, and search in Claude directories failed.\nDetail: {err}", file=sys.stderr)
            sys.exit(1)
        file_path = detected_file
        print(f"[*] Found and parsing matching session file: {file_path}")
        
    events, err = parse_session_file(file_path)
    if err:
        print(f"Error parsing session file: {err}", file=sys.stderr)
        sys.exit(1)
        
    analysis = analyze_session(events)
    
    print("\n" + "="*50)
    print("           CLAUDE CODE SESSION ANALYSIS")
    print("="*50)
    print(f"Session ID:         {analysis['session_id']}")
    print(f"Git Branch:         {analysis['git_branch']}")
    print(f"Workspace (CWD):    {analysis['cwd']}")
    print(f"Has Error:          {analysis['has_error']}")
    print(f"Interruption:       {analysis['interruption_reason']}")
    if analysis['last_prompt']:
        print(f"Last Prompt Logged: {analysis['last_prompt']}")
    print("="*50 + "\n")
    
    # Write HANDOFF.md
    handoff_text = analysis["latest_handoff_content"]
    source_type = "Extracted from attachment"
    
    if not handoff_text:
        handoff_text = build_fallback_handoff(analysis)
        source_type = "Synthesized from session timeline"
        
    out_path = args.out
    if not out_path:
        out_path = os.path.join(project_path, "HANDOFF.md")
        
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(handoff_text)
        print(f"[+] Successfully wrote {out_path} ({source_type})")
    except Exception as e:
        print(f"[-] Error writing {out_path}: {e}", file=sys.stderr)
        
    # Output the copy-paste resumption snippet
    rel_handoff_path = os.path.relpath(out_path, project_path)
    print("\n" + "#"*60)
    print("   READY TO RESUME. COPY AND PASTE THE FOLLOWING INSTRUCTION:")
    print("#"*60)
    print(f"\n我们继续上一个 Agent Session (Claude Code CLI) 的操作。")
    print(f"中断原因：{analysis['interruption_reason']}")
    print(f"交接指令在 [{rel_handoff_path}](file://{os.path.abspath(out_path)}) ，请先读取它，并按该文件的指示接续任务进行操作。\n")
    print("#"*60 + "\n")
    
    # Print genuine work rounds
    print("="*50)
    print("      LAST 10 GENUINE WORK ACTIONS (断点精确参考)")
    print("="*50)
    recent_work = analysis.get("genuine_work", [])[-10:]
    if recent_work:
        for idx, w in enumerate(recent_work):
            print(f"[{idx}] TS: {w['timestamp']} | Role: {w['role']}")
            if w['tools']:
                print(f"  Tools: {w['tools']}")
            snippet = w['content'].replace('\n', ' ')
            print(f"  Text:  {snippet[:120]}...")
            print("-" * 30)
    else:
        print("  *(No genuine file editing or test actions detected.)*")
    print("="*50 + "\n")
    
    # Print dialogue history
    print(f"Recent Dialogue (Showing up to {args.rounds} rounds):")
    recent_dialogue = analysis["dialogue"][-args.rounds * 2:]
    for r in recent_dialogue:
        role_label = f"[{r['timestamp']}] {r['role']}"
        print(f"\n{role_label}:")
        print("-" * len(role_label))
        print(r["content"])
        print("-" * 20)

if __name__ == "__main__":
    main()
