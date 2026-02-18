#!/usr/bin/env python3
import subprocess
import sys
import datetime
import os
import argparse

def run_cmd(cmd, check=True):
    """运行 shell 命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error executing: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def get_commit_info(commit_hash):
    """获取指定 commit 的时间和 message"""
    return run_cmd(f"git show -s --format='%ci | %s' {commit_hash}")

def append_to_archive_md(content):
    """追加内容到根目录的 ARCHIVE.md"""
    file_path = "ARCHIVE.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mode = "a" if os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        f.write(f"\n## [{timestamp}] 存档记录\n")
        f.write(content + "\n")
        f.write("-" * 40 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Git Snapshot & Rollback")
    parser.add_argument("target_commit", help="要回退到的目标 Commit Hash")
    parser.add_argument("reason", help="回退的原因")
    parser.add_argument("--push", action="store_true", help="是否推送到远程仓库")
    args = parser.parse_args()

    target_commit = args.target_commit
    reason = args.reason
    should_push = args.push

    # 1. 获取环境信息
    current_branch = run_cmd("git rev-parse --abbrev-ref HEAD")
    
    # --- Phase 1: Archive ---
    print(f"[*] Phase 1: Archiving current state...")
    
    # Commit uncommitted changes
    status = run_cmd("git status --porcelain", check=False)
    if status:
        run_cmd("git add .")
        run_cmd(f"git commit -m 'WIP: Auto-save before rollback to {target_commit[:7]}'")
    
    source_commit = run_cmd("git rev-parse HEAD")
    source_commit_info = get_commit_info(source_commit)
    
    time_suffix = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    archive_branch = f"archive/{current_branch}/{time_suffix}"
    
    run_cmd(f"git checkout -b {archive_branch}")
    
    target_info = get_commit_info(target_commit)
    archive_log = f"""
- **动作**: 准备回退
- **原因**: {reason}
- **当前分支**: {current_branch}
- **生成的存档分支**: `{archive_branch}`
- **回退目标 (Target)**: `{target_commit[:7]}`
- **目标详情**: {target_info}
"""
    append_to_archive_md(archive_log)
    run_cmd("git add ARCHIVE.md")
    run_cmd(f"git commit -m 'Archive: Rollback from {current_branch} to {target_commit[:7]} due to {reason}'")
    
    if should_push:
        try:
            run_cmd(f"git push -u origin {archive_branch}")
            print(f"[*] Pushed archive branch: {archive_branch}")
        except:
            print("[!] Warning: Push failed, skipping.")
    else:
        print("[*] Push skipped as requested.")

    # --- Phase 2: Land ---
    print(f"[*] Phase 2: Resetting {current_branch}...")
    run_cmd(f"git checkout {current_branch}")
    run_cmd(f"git reset --hard {target_commit}")
    
    reset_log = f"""
- **动作**: 回退完成
- **原因**: {reason}
- **来源存档分支**: `{archive_branch}`
- **回退的分支**: {current_branch}
- **来源 Commit**: `{source_commit[:7]}`
- **来源详情**: {source_commit_info}
"""
    append_to_archive_md(reset_log)
    run_cmd("git add ARCHIVE.md")
    run_cmd(f"git commit -m 'Reset: Landed from {archive_branch} ({source_commit[:7]}) due to {reason}'")

    print(f"[SUCCESS] Rollback completed. Check ARCHIVE.md for details.")
    
    # 3. 列出所有未推送的分支
    print("\n[*] 检查本地未推送的分支 (Ahead of remote):")
    unpushed = run_cmd("git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads | grep 'ahead' || true", check=False)
    if unpushed:
        print(unpushed)
    else:
        print("(None)")

if __name__ == "__main__":
    main()
