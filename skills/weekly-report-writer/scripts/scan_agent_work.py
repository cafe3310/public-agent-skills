#!/usr/bin/env python3
"""
scan_agent_work.py
扫描周期内工作区 Git 仓库提交历史与 Antigravity 会话记录，提取潜在的 ❇️（代码/Agent 侧工作）候选项。
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

def scan_git_repos(workspace_dir, since_date):
    results = {}
    if not os.path.exists(workspace_dir):
        return results

    for name in sorted(os.listdir(workspace_dir)):
        repo_path = os.path.join(workspace_dir, name)
        if not os.path.isdir(repo_path) or not os.path.isdir(os.path.join(repo_path, ".git")):
            continue

        try:
            log_output = subprocess.check_output(
                ["git", "log", f"--since={since_date}", "--oneline", "-n", "20"],
                cwd=repo_path,
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            if log_output:
                results[name] = log_output.splitlines()
        except Exception:
            continue

    return results

def scan_antigravity_sessions(brain_dir, since_dt):
    sessions = []
    if not os.path.exists(brain_dir):
        return sessions

    for item in os.listdir(brain_dir):
        session_path = os.path.join(brain_dir, item)
        if not os.path.isdir(session_path) or item.startswith("."):
            continue

        transcript_path = os.path.join(session_path, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue

        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(transcript_path))
            if mtime < since_dt:
                continue

            first_prompt = ""
            created_at = ""
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        step = json.loads(line)
                        if step.get("type") == "USER_INPUT":
                            first_prompt = step.get("content", "").strip().replace("\n", " ")[:120]
                            created_at = step.get("created_at", "")[:16]
                            break
                    except Exception:
                        continue

            if first_prompt:
                # 过滤明显无独立工程产出的侧边问答或测试
                is_side_question = "This is a side question from the user" in first_prompt
                sessions.append({
                    "id": item,
                    "created_at": created_at,
                    "prompt": first_prompt,
                    "is_side_question": is_side_question
                })
        except Exception:
            continue

    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions

def main():
    parser = argparse.ArgumentParser(description="扫描工作区 Git 提交与 Antigravity 会话")
    parser.add_argument("--since", required=True, help="起始日期 (YYYY-MM-DD)")
    parser.add_argument("--workspace", default=os.path.expanduser("~/workspace"), help="工作区根目录")
    parser.add_argument("--brain", default=os.path.expanduser("~/.gemini/antigravity/brain"), help="Antigravity brain 目录")
    args = parser.parse_args()

    try:
        since_dt = datetime.strptime(args.since, "%Y-%m-%d")
    except ValueError:
        print(f"错误: 无法解析日期格式 '{args.since}'，请使用 YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)

    print(f"=== 扫描周期起始: {args.since} ===\n")

    print("### 1. 工作区活跃 Git 仓库提交")
    git_results = scan_git_repos(args.workspace, args.since)
    if not git_results:
        print("未检测到周期内的 Git 提交。\n")
    else:
        for repo, commits in git_results.items():
            print(f"- **{repo}** ({len(commits)} commits):")
            for c in commits[:5]:
                print(f"  - {c}")
            if len(commits) > 5:
                print(f"  - ... (其余 {len(commits) - 5} 条省略)")
        print()

    print("### 2. Antigravity 活跃会话任务")
    sessions = scan_antigravity_sessions(args.brain, since_dt)
    effective_sessions = [s for s in sessions if not s["is_side_question"]]
    if not effective_sessions:
        print("未检测到周期内的工程类 Antigravity 会话。\n")
    else:
        for s in effective_sessions:
            print(f"- [{s['created_at']}] `{s['id'][:8]}`: {s['prompt']}")
        print()

if __name__ == "__main__":
    main()
