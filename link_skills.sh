#!/bin/bash

# 当前目录下的 skills 路径
SOURCE_BASE="$(pwd)/skills"

if [ ! -d "$SOURCE_BASE" ]; then
    echo "错误：当前目录下未找到 'skills' 文件夹。"
    exit 1
fi

# 目标基础目录探测
TARGET_SKILLS_DIRS=()

# 自动探测存在的基础目录，并加入目标列表
for base_dir in "~/.agents" "~/.claude" "~/.gemini/antigravity-cli" "~/.gemini"; do
    expanded_dir="${base_dir/#\~/$HOME}"
    if [ -d "$expanded_dir" ]; then
        TARGET_SKILLS_DIRS+=("$expanded_dir/skills")
    fi
done

# 如果未探测到任何基础目录，默认创建并安装到 ~/.agents/skills 与 ~/.gemini/antigravity-cli/skills
if [ ${#TARGET_SKILLS_DIRS[@]} -eq 0 ]; then
    TARGET_SKILLS_DIRS+=("$HOME/.agents/skills" "$HOME/.gemini/antigravity-cli/skills")
fi

echo "--- 配置安装路径 ---"
echo "将要把 skills 安装到以下目录："
for target in "${TARGET_SKILLS_DIRS[@]}"; do
    echo "  - $target"
done
echo

# --- 增加全局确认逻辑 ---
echo "即将执行以下操作："
echo "1. 将 $SOURCE_BASE 下的技能软链接到上述目录"
echo "2. 将生成的软链接添加到对应目录的 .gitignore"
echo "3. 尝试从 Git 版本控制中移除已有的软链接（git rm --cached）"
echo
read -p "是否确定继续？(y/N) " global_confirm
if [[ "$global_confirm" != "y" && "$global_confirm" != "Y" ]]; then
    echo "操作已取消。"
    exit 0
fi

# 确保所有目标目录存在
for target_dir in "${TARGET_SKILLS_DIRS[@]}"; do
    mkdir -p "$target_dir"
done

echo "正在批量链接技能..."
echo "------------------------------------------------"

# 遍历 source 目录下的所有子目录
for skill_dir in "$SOURCE_BASE"/*; do
    # 确保它是一个目录
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")

        # 链接至每个目标目录
        for target_dir in "${TARGET_SKILLS_DIRS[@]}"; do
            target_link="$target_dir/$skill_name"

            # 检查技能目录链接
            if [ -L "$target_link" ] && [ ! -e "$target_link" ]; then
                # 如果是损坏的软链接，则直接覆盖
                ln -sf "$skill_dir" "$target_link"
                echo " [覆盖无效链接] $skill_name -> $target_link"
            elif [ -e "$target_link" ] || [ -L "$target_link" ]; then
                echo " [跳过技能] $skill_name (在 $target_dir 已存在)"
            else
                ln -s "$skill_dir" "$target_link"
                echo " [创建技能] $skill_name -> $target_link"
            fi

            # --- 增加 Git 忽略和清理逻辑 ---
            IS_GIT_REPO=false
            if [ -d "$(dirname "$target_dir")/.git" ] || [ -d "$target_dir/.git" ]; then
                IS_GIT_REPO=true
            fi

            if [ "$IS_GIT_REPO" = true ]; then
                # 添加到 .gitignore (如果不存在)
                GITIGNORE_PATH="$target_dir/.gitignore"
                if ! grep -qxF "$skill_name" "$GITIGNORE_PATH" 2>/dev/null; then
                    echo "$skill_name" >> "$GITIGNORE_PATH"
                    echo " [Git] 已将 $skill_name 添加到 $GITIGNORE_PATH"
                fi
                # 从 Git 缓存中移除 (防止之前已被提交)
                (cd "$target_dir" && git rm --cached -r "$skill_name" 2>/dev/null && echo " [Git] 已从缓存中从 $target_dir 移除") || true
            fi
        done
    fi
done

echo "------------------------------------------------"
echo "处理完成。"
