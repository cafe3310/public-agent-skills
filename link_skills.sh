#!/bin/bash

# 目标基础目录
TARGET_BASE="$HOME/.gemini/skills"
# 当前目录下的 skills 路径
SOURCE_BASE="$(pwd)/skills"

# 确保目标基础目录存在
mkdir -p "$TARGET_BASE"

if [ ! -d "$SOURCE_BASE" ]; then
    echo "错误：当前目录下未找到 'skills' 文件夹。"
    exit 1
fi

echo "正在从 $SOURCE_BASE 批量链接技能到 $TARGET_BASE ..."
echo "------------------------------------------------"

# 遍历 source 目录下的所有子目录
for skill_dir in "$SOURCE_BASE"/*; do
    # 确保它是一个目录
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        target_link="$TARGET_BASE/$skill_name"

        # 检查目标是否已存在（包括符号链接）
        if [ -e "$target_link" ] || [ -L "$target_link" ]; then
            echo " [跳过] $skill_name (目标已存在: $target_link)"
        else
            # 创建符号链接
            ln -s "$skill_dir" "$target_link"
            echo " [创建] $skill_name -> $target_link"
        fi
    fi
done

echo "------------------------------------------------"
echo "处理完成。"
