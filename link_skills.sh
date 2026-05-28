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
echo "1. 将 $SOURCE_BASE 下的技能以物理目录形式安装/同步到上述目录"
echo "   (当目标中已存在且有差异时，会交互式提示您确认覆盖)"
echo "2. 将安装的技能目录添加到对应目录的 .gitignore"
echo "3. 尝试从 Git 版本控制中移除对应目录缓存（git rm --cached）"
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

echo "正在批量安装/同步技能..."
echo "------------------------------------------------"

# 遍历 source 目录下的所有子目录
for skill_dir in "$SOURCE_BASE"/*; do
    # 确保它是一个目录
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")

        # 安装至每个目标目录
        for target_dir in "${TARGET_SKILLS_DIRS[@]}"; do
            target_skill_dir="$target_dir/$skill_name"

            # 1. 软链接强制替换为物理复制
            if [ -L "$target_skill_dir" ]; then
                rm -f "$target_skill_dir"
                cp -r "$skill_dir" "$target_skill_dir"
                echo " [覆盖软链接] $skill_name -> $target_skill_dir"
            
            # 2. 目标真实目录存在，执行 diff 校验
            elif [ -d "$target_skill_dir" ]; then
                diff_output=$(diff -r -q "$skill_dir" "$target_skill_dir" 2>&1)
                diff_status=$?
                
                if [ $diff_status -eq 0 ]; then
                    echo " [一致跳过] $skill_name (内容一致，无需更新)"
                else
                    echo -e "\033[1;33m⚠️  检测到 $skill_name 在目标中存在差异：\033[0m"
                    echo "$diff_output" | sed 's/^/    /'
                    
                    read -p "是否覆盖目标 $target_skill_dir ？(y/N) " confirm_overwrite
                    if [[ "$confirm_overwrite" == "y" || "$confirm_overwrite" == "Y" ]]; then
                        rm -rf "$target_skill_dir"
                        cp -r "$skill_dir" "$target_skill_dir"
                        echo " [更新技能] $skill_name (已物理覆盖)"
                    else
                        echo " [保留旧版] $skill_name (已跳过)"
                    fi
                fi
            
            # 3. 目标不存在，直接物理复制
            else
                cp -r "$skill_dir" "$target_skill_dir"
                echo " [新建安装] $skill_name -> $target_skill_dir"
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
