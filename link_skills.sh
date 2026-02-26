#!/bin/bash

# 目标基础目录
TARGET_SKILLS="$HOME/.gemini/skills"
TARGET_AGENTS="$HOME/.gemini/agents"
# 当前目录下的 skills 路径
SOURCE_BASE="$(pwd)/skills"

# 确保目标基础目录存在
mkdir -p "$TARGET_SKILLS"
mkdir -p "$TARGET_AGENTS"

if [ ! -d "$SOURCE_BASE" ]; then
    echo "错误：当前目录下未找到 'skills' 文件夹。"
    exit 1
fi

# --- 增加全局确认逻辑 ---
echo "即将执行以下操作："
echo "1. 将 $SOURCE_BASE 下的技能软链接到 $TARGET_SKILLS"
echo "2. 将生成的软链接添加到 $TARGET_SKILLS/.gitignore"
echo "3. 尝试从 Git 版本控制中移除已有的软链接（git rm --cached）"
echo "4. 物理复制 Sub-agents 到 $TARGET_AGENTS"
echo
read -p "是否确定继续？(y/N) " global_confirm
if [[ "$global_confirm" != "y" && "$global_confirm" != "Y" ]]; then
    echo "操作已取消。"
    exit 0
fi

echo "正在从 $SOURCE_BASE 批量链接技能到 $TARGET_SKILLS ..."
echo "------------------------------------------------"

# 检查目标目录是否在 Git 管理下
IS_GIT_REPO=false
if [ -d "$(dirname "$TARGET_SKILLS")/.git" ] || [ -d "$TARGET_SKILLS/.git" ]; then
    IS_GIT_REPO=true
fi

# 遍历 source 目录下的所有子目录
for skill_dir in "$SOURCE_BASE"/*; do
    # 确保它是一个目录
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        target_link="$TARGET_SKILLS/$skill_name"

        # 检查技能目录链接
        if [ -e "$target_link" ] || [ -L "$target_link" ]; then
            echo " [跳过技能] $skill_name (目标已存在)"
        else
            ln -s "$skill_dir" "$target_link"
            echo " [创建技能] $skill_name -> $target_link"
        fi

        # --- 增加 Git 忽略和清理逻辑 ---
        if [ "$IS_GIT_REPO" = true ]; then
            # 添加到 .gitignore (如果不存在)
            GITIGNORE_PATH="$TARGET_SKILLS/.gitignore"
            if ! grep -qxF "$skill_name" "$GITIGNORE_PATH" 2>/dev/null; then
                echo "$skill_name" >> "$GITIGNORE_PATH"
                echo " [Git] 已将 $skill_name 添加到 .gitignore"
            fi
            # 从 Git 缓存中移除 (防止之前已被提交)
            (cd "$TARGET_SKILLS" && git rm --cached -r "$skill_name" 2>/dev/null && echo " [Git] 已从缓存中移除 $skill_name") || true
        fi

        # 处理该技能下的 agents 目录
        agents_source_dir="$skill_dir/agents"
        if [ -d "$agents_source_dir" ]; then
            for agent_file in "$agents_source_dir"/*.md; do
                if [ -f "$agent_file" ]; then
                    agent_name=$(basename "$agent_file")
                    agent_target="$TARGET_AGENTS/$agent_name"

                    if [ -e "$agent_target" ]; then
                        read -p " [确认] Agent $agent_name 已存在，是否覆盖？(y/N) " confirm
                        if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                            cp -f "$agent_file" "$agent_target"
                            echo " [覆盖 Agent] $agent_name -> $agent_target"
                        else
                            echo " [跳过 Agent] $agent_name"
                        fi
                    else
                        cp -f "$agent_file" "$agent_target"
                        echo " [安装 Agent] $agent_name -> $agent_target"
                    fi
                fi
            done
        fi
    fi
done

echo "------------------------------------------------"
echo -e "\033[1;33m⚠️  重要提醒：\033[0m"
echo -e "\033[1;31mSub-agents 在当前环境下必须使用物理复制（Copy）而非软链接（Link）。\033[0m"
echo -e "\033[1;31m本次操作已根据您的确认覆盖了已有的 Sub-agent 文件。\033[0m"
echo "------------------------------------------------"
echo "处理完成。"
