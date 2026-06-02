#!/usr/bin/env python3
import os
import sys
import json
import shutil
import datetime
import subprocess
import difflib

# ------------------------------------------------
# Constants and Path Settings
# ------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_BASE = os.path.join(SCRIPT_DIR, "skills")
SOURCE_PARKED = os.path.join(SCRIPT_DIR, "skills_parked")
SOURCE_AGENTS_MD = os.path.join(SCRIPT_DIR, "GLOBAL_AGENTS.md")

GLOBAL_AGENTS_MAPPING = {
    "~/.agents": "AGENTS.md",
    "~/.claude": "CLAUDE.md",
    "~/.gemini/antigravity-cli": "GEMINI.md",
    "~/.gemini": "GEMINI.md"
}

# ------------------------------------------------
# Git Helper Functions
# ------------------------------------------------
def get_git_info():
    remote_url = "local-repository"
    commit_hash = "unknown"
    commit_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True, cwd=SCRIPT_DIR)
        remote_url = res.stdout.strip()
    except Exception:
        pass
        
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=SCRIPT_DIR)
        commit_hash = res.stdout.strip()
    except Exception:
        pass
        
    try:
        res = subprocess.run(["git", "log", "-1", "--format=%ci"], capture_output=True, text=True, check=True, cwd=SCRIPT_DIR)
        commit_datetime = res.stdout.strip()
    except Exception:
        pass
        
    return remote_url, commit_hash, commit_datetime

# ------------------------------------------------
# TUI Keyboard and Choice Component
# ------------------------------------------------
def get_char():
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def select_parked_skills(skills):
    if not skills:
        return []
    
    selected = [False] * len(skills)
    index = 0
    
    print("\n请选择要同步的 Parked Skills (按 [Enter] 确认选择，[Ctrl+C] 退出):")
    # 先预留空白行用于渲染
    for _ in range(len(skills)):
        print()
        
    # 隐藏光标
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        while True:
            # 清理之前的输出（向上移 N 行并清除）
            for _ in range(len(skills)):
                sys.stdout.write("\033[F\033[K")
            
            for i, skill in enumerate(skills):
                marker = "[x]" if selected[i] else "[ ]"
                if i == index:
                    print(f" > \033[1;36m{marker} {skill}\033[0m")
                else:
                    print(f"   {marker} {skill}")
            sys.stdout.flush()
            
            key = get_char()
            if key == '\x1b[A':   # Up arrow
                index = (index - 1) % len(skills)
            elif key == '\x1b[B': # Down arrow
                index = (index + 1) % len(skills)
            elif key == ' ':       # Spacebar
                selected[index] = not selected[index]
            elif key in ('\r', '\n'): # Enter
                break
            elif key == '\x03': # Ctrl+C
                raise KeyboardInterrupt
    finally:
        sys.stdout.write("\033[?25h") # 恢复光标
        sys.stdout.flush()
        
    return [skills[i] for i in range(len(skills)) if selected[i]]

# ------------------------------------------------
# Diff Side-by-Side Component
# ------------------------------------------------
def display_side_by_side_diff(old_path, new_path):
    try:
        with open(old_path, "r", encoding="utf-8", errors="ignore") as f:
            old_lines = f.read().splitlines()
        with open(new_path, "r", encoding="utf-8", errors="ignore") as f:
            new_lines = f.read().splitlines()
    except Exception as e:
        print(f" [错误] 读取对比文件失败: {e}")
        return False
        
    diff = list(difflib.ndiff(old_lines, new_lines))
    term_width = 120
    col_width = (term_width - 5) // 2
    
    print("-" * term_width)
    print(f"{'CURRENT FILE (LEFT)':<{col_width}} | {'NEW FILE (RIGHT)':<{col_width}}")
    print("-" * term_width)
    
    for line in diff:
        prefix = line[:2]
        content = line[2:]
        display_content = content[:col_width]
        
        if prefix == "  ":
            print(f"{display_content:<{col_width}} | {display_content:<{col_width}}")
        elif prefix == "- ":
            colored = f"\033[31m{display_content}\033[0m"
            padding = " " * (col_width - len(display_content))
            print(f"{colored}{padding} | {' ' * col_width}")
        elif prefix == "+ ":
            colored = f"\033[32m{display_content}\033[0m"
            print(f"{' ' * col_width} | {colored}")
            
    print("-" * term_width)
    return True

# ------------------------------------------------
# Safe Delete Utility
# ------------------------------------------------
def safe_delete(path):
    if not os.path.exists(path) and not os.path.islink(path):
        return False
        
    name = os.path.basename(path)
    
    # 1. First priority: trash
    if shutil.which("trash"):
        try:
            subprocess.run(["trash", path], check=True)
            print(f"  [失效清理] 已使用系统 `trash` 工具将 {name} 移入系统废纸篓")
            return True
        except Exception:
            pass
            
    # 2. Second priority: gomi
    if shutil.which("gomi"):
        try:
            subprocess.run(["gomi", path], check=True)
            print(f"  [失效清理] 已使用 `gomi` 工具将 {name} 移入垃圾箱")
            return True
        except Exception:
            pass
            
    # 3. Third priority: fallback move to ~/YYYYMMDDhhmmss-removed-skill
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = os.path.expanduser(f"~/{timestamp}-removed-skill")
    os.makedirs(backup_root, exist_ok=True)
    
    dest_path = os.path.join(backup_root, name)
    try:
        # Move directory or file/symlink
        shutil.move(path, dest_path)
        print(f"  [失效清理] 未配备 trash/gomi，已将 {name} 安全移动到备份路径：{dest_path}")
        return True
    except Exception as e:
        print(f"  [错误] 备份移动失败 {path}: {e}")
        
    # Last ditch try to remove normally if everything failed
    try:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except Exception:
        return False

# ------------------------------------------------
# Sync Execution Logic
# ------------------------------------------------
def main():
    if not os.path.isdir(SOURCE_BASE):
        print(f"错误：源技能目录 '{SOURCE_BASE}' 不存在。")
        sys.exit(1)
        
    remote_url, commit_hash, commit_datetime = get_git_info()
    
    print("=========================================")
    print("    Agent Skills Python Sync Utility     ")
    print("=========================================")
    print(f"仓库: {remote_url}")
    print(f"提交: {commit_hash[:8]} ({commit_datetime})")
    print("=========================================\n")
    
    # --------------------------------------------
    # Part 1. Update Global Config Files
    # --------------------------------------------
    print("--- 步骤 1: 全局 Agent 规则检查 ---")
    if os.path.exists(SOURCE_AGENTS_MD):
        for raw_path, target_name in GLOBAL_AGENTS_MAPPING.items():
            expanded = os.path.expanduser(raw_path)
            if os.path.isdir(expanded):
                target_file = os.path.join(expanded, target_name)
                print(f"\n正在检查 {target_file} ...")
                
                # Check diff
                needs_update = False
                if not os.path.exists(target_file):
                    print("  [未找到目标配置] 标记为全新配置。")
                    needs_update = True
                else:
                    # Compare content
                    try:
                        with open(SOURCE_AGENTS_MD, "r", encoding="utf-8") as f:
                            src_c = f.read()
                        with open(target_file, "r", encoding="utf-8") as f:
                            tgt_c = f.read()
                        if src_c != tgt_c:
                            needs_update = True
                    except Exception:
                        needs_update = True
                
                if needs_update:
                    if os.path.exists(target_file):
                        print("  [检测到差异] 展示文件变更比对（左侧为原配置，右侧为新配置）:")
                        display_side_by_side_diff(target_file, SOURCE_AGENTS_MD)
                        
                        confirm = input(f"是否覆盖此文件？({target_file}) [y/N]: ").strip().lower()
                        if confirm != 'y':
                            print("  [跳过] 用户选择不覆盖。")
                            continue
                    
                    # Force delete existing to sever symlinks, then physical copy
                    if os.path.exists(target_file) or os.path.islink(target_file):
                        if os.path.islink(target_file):
                            os.remove(target_file)
                        else:
                            safe_delete(target_file)
                            
                    try:
                        shutil.copy2(SOURCE_AGENTS_MD, target_file)
                        print(f"  [物理覆盖成功] {target_file}")
                    except Exception as e:
                        print(f"  [覆盖失败] {target_file}: {e}")
                else:
                    print("  [一致跳过] 内容完全一致，无需更新。")
    else:
        print("未找到 GLOBAL_AGENTS.md，跳过全局规则更新。")
        
    # --------------------------------------------
    # Part 2. Synchronize Skills
    # --------------------------------------------
    print("\n--- 步骤 2: 目标路径探测与 Skills 同步 ---")
    targets_detected = []
    for raw_path in ["~/.agents", "~/.claude", "~/.gemini/antigravity-cli", "~/.gemini"]:
        expanded = os.path.expanduser(raw_path)
        if os.path.isdir(expanded):
            targets_detected.append(expanded)
            
    if not targets_detected:
        targets_detected = [os.path.expanduser("~/.agents"), os.path.expanduser("~/.gemini/antigravity-cli")]
        
    print(f"已探测到的目标配置路径：")
    for t in targets_detected:
        print(f"  - {t}")
        
    # 扫描本仓库的 Active Skills 和 Parked Skills
    active_skills = [d for d in os.listdir(SOURCE_BASE) if os.path.isdir(os.path.join(SOURCE_BASE, d)) and d not in (".git", ".idea", "__pycache__")]
    
    parked_skills = []
    if os.path.isdir(SOURCE_PARKED):
        parked_skills = [d for d in os.listdir(SOURCE_PARKED) if os.path.isdir(os.path.join(SOURCE_PARKED, d))]
        
    # 交互式选择 Parked Skills
    selected_parked = []
    if parked_skills:
        try:
            selected_parked = select_parked_skills(parked_skills)
        except (KeyboardInterrupt, SystemExit):
            print("\n已取消选择 Parked Skills。")
            sys.exit(0)
    skipped_parked = [p for p in parked_skills if p not in selected_parked]
    
    # 逐个目标目录进行处理
    reports = {}
    
    for target_base in targets_detected:
        skills_dest = os.path.join(target_base, "skills")
        os.makedirs(skills_dest, exist_ok=True)
        
        json_path = os.path.join(target_base, "cafe3310-managed-skills.json")
        
        # 1. 读取或初始化 JSON 状态
        managed_data = {
            "description": "Managed skills index for cafe3310's agent toolchain.",
            "repositories": {}
        }
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    managed_data = json.load(f)
            except Exception:
                print(f" ⚠️  {json_path} 解析失败，将自动覆盖/新创建。")
        else:
            print(f"  [新配置] 未在 {target_base} 找到状态文件，正在自动创建。")
            
        repo_records = managed_data.get("repositories", {})
        
        # 2. 冲突检测与同步计划
        staged_sync = [] # 元组: (name, type, src_path, status)
        
        # 检查 Active Skills
        for skill in active_skills:
            src_p = os.path.join(SOURCE_BASE, skill)
            dest_p = os.path.join(skills_dest, skill)
            
            if os.path.exists(dest_p) or os.path.islink(dest_p):
                # 判断当前技能是否属于本仓库管理
                is_managed_by_me = False
                if remote_url in repo_records:
                    if skill in repo_records[remote_url].get("skills", []) or skill in repo_records[remote_url].get("selected-parked-skills", []):
                        is_managed_by_me = True
                
                # 检查其他仓库有没有管理
                managed_by_other = False
                other_repo = None
                for r_url, val in repo_records.items():
                    if r_url != remote_url:
                        if skill in val.get("skills", []) or skill in val.get("selected-parked-skills", []):
                            managed_by_other = True
                            other_repo = r_url
                            break
                            
                if is_managed_by_me:
                    staged_sync.append((skill, "active", src_p, "safe-overwrite"))
                elif managed_by_other:
                    print(f" \033[1;31m[冲突] 技能 {skill} 正被其他仓库管理: {other_repo}。同步跳过。\033[0m")
                else:
                    confirm_takeover = input(f"  [接管确认] 目标中已存在 {skill} 但未被任何仓库标记管理。是否由本仓库接管？[y/N]: ").strip().lower()
                    if confirm_takeover == 'y':
                        staged_sync.append((skill, "active", src_p, "safe-overwrite"))
                    else:
                        print(f"  [跳过] 技能 {skill} 同步跳过以防止误覆盖。")
            else:
                staged_sync.append((skill, "active", src_p, "add"))
                
        # 检查选中的 Parked Skills
        for skill in selected_parked:
            src_p = os.path.join(SOURCE_PARKED, skill)
            dest_p = os.path.join(skills_dest, skill)
            
            if os.path.exists(dest_p) or os.path.islink(dest_p):
                is_managed_by_me = False
                if remote_url in repo_records:
                    if skill in repo_records[remote_url].get("skills", []) or skill in repo_records[remote_url].get("selected-parked-skills", []):
                        is_managed_by_me = True
                        
                managed_by_other = False
                other_repo = None
                for r_url, val in repo_records.items():
                    if r_url != remote_url:
                        if skill in val.get("skills", []) or skill in val.get("selected-parked-skills", []):
                            managed_by_other = True
                            other_repo = r_url
                            break
                            
                if is_managed_by_me:
                    staged_sync.append((skill, "parked", src_p, "safe-overwrite"))
                elif managed_by_other:
                    print(f" \033[1;31m[冲突] Parked 技能 {skill} 正被其他仓库管理: {other_repo}。同步跳过。\033[0m")
                else:
                    confirm_takeover = input(f"  [接管确认] 目标中已存在 Parked 技能 {skill} 但未被任何仓库标记管理。是否由本仓库接管？[y/N]: ").strip().lower()
                    if confirm_takeover == 'y':
                        staged_sync.append((skill, "parked", src_p, "safe-overwrite"))
                    else:
                        print(f"  [跳过] Parked 技能 {skill} 同步跳过以防止误覆盖。")
            else:
                staged_sync.append((skill, "parked", src_p, "add"))
                
        # 3. 清理失效残留技能
        staged_cleanup = []
        my_prev_managed = []
        if remote_url in repo_records:
            my_prev_managed = repo_records[remote_url].get("skills", []) + repo_records[remote_url].get("selected-parked-skills", [])
            
        current_sync_names = active_skills + selected_parked
        for prev_skill in my_prev_managed:
            if prev_skill not in current_sync_names:
                prev_dest_p = os.path.join(skills_dest, prev_skill)
                if os.path.exists(prev_dest_p) or os.path.islink(prev_dest_p):
                    staged_cleanup.append(prev_skill)
                    
        # 4. 执行文件操作
        report_details = {
            "add": [],
            "overwrite": [],
            "add_parked": [],
            "overwrite_parked": [],
            "cleaned": []
        }
        
        # 执行复制/覆盖
        for skill_name, sk_type, src_p, status in staged_sync:
            dest_p = os.path.join(skills_dest, skill_name)
            
            # 断开可能存在的文件/软链接
            if os.path.exists(dest_p) or os.path.islink(dest_p):
                if os.path.islink(dest_p):
                    os.remove(dest_p)
                else:
                    # 使用 trash 进行安全替代
                    safe_delete(dest_p)
                    
            try:
                shutil.copytree(src_p, dest_p, symlinks=False)
                if status == "add":
                    if sk_type == "active":
                        report_details["add"].append(skill_name)
                    else:
                        report_details["add_parked"].append(skill_name)
                else:
                    if sk_type == "active":
                        report_details["overwrite"].append(skill_name)
                    else:
                        report_details["overwrite_parked"].append(skill_name)
            except Exception as e:
                print(f" [错误] 复制技能 {skill_name} 失败: {e}")
                
        # 执行失效清理
        if staged_cleanup:
            print(f"\n在目标 {target_base} 检测到已被移除或取消选择的失效技能：")
            for cl_sk in staged_cleanup:
                print(f"  - {cl_sk}")
            confirm_clean = input("是否执行安全清理？(用 trash/备份 移除) [y/N]: ").strip().lower()
            if confirm_clean == 'y':
                for cl_sk in staged_cleanup:
                    prev_dest_p = os.path.join(skills_dest, cl_sk)
                    if safe_delete(prev_dest_p):
                        report_details["cleaned"].append(cl_sk)
                        
        # 5. 更新并写回 JSON 状态
        repo_records[remote_url] = {
            "commit": {
                "hash": commit_hash,
                "datetime": commit_datetime
            },
            "skills": active_skills,
            "selected-parked-skills": selected_parked,
            "skipped-parked-skills": skipped_parked
        }
        managed_data["repositories"] = repo_records
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(managed_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" [错误] 更新状态 JSON 失败: {e}")
            
        reports[target_base] = report_details
        
    # --------------------------------------------
    # Part 3. Print Final Summarized Report
    # --------------------------------------------
    print("\n" + "=" * 50)
    print("                同步状态汇总                 ")
    print("=" * 50)
    for target_base, details in reports.items():
        print(f"\n[目标目录] {target_base}/skills")
        print(f"  - 添加的活跃:      {details['add']}")
        print(f"  - 安全覆盖活跃:    {details['overwrite']}")
        print(f"  - 添加的 Parked:   {details['add_parked']}")
        print(f"  - 安全覆盖 Parked: {details['overwrite_parked']}")
        print(f"  - 清理的失效:      {details['cleaned']}")
    print("=" * 50 + "\n")
    print("同步完成。")

if __name__ == "__main__":
    main()
