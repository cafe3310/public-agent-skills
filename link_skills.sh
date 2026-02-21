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

echo "正在从 $SOURCE_BASE 批量链接技能到 $TARGET_SKILLS ..."
echo "------------------------------------------------"

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
