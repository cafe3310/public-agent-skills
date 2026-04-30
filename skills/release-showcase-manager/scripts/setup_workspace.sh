#!/bin/bash
# 脚本：setup_workspace.sh
# 用途：初始化 release-showcase-manager 技能所需的项目工作区结构

TARGET_DIR=${1:-.}
TEMPLATE_DIR="$(dirname "$0")/../assets/template_workspace"

echo "正在初始化工作区：$TARGET_DIR"

# 创建目录结构
mkdir -p "$TARGET_DIR"/{docs-and-ref,notes,showcases,video-raw,video-clipped}

# 检查并初始化 Git LFS
if [ -d "$TARGET_DIR/.git" ]; then
    echo "检测到 Git 仓库，正在配置 LFS..."
    git -C "$TARGET_DIR" lfs install
    git -C "$TARGET_DIR" lfs track "*.mp4" "*.mov" "*.avi" "*.mkv"
    if [ ! -f "$TARGET_DIR/.gitattributes" ]; then
        echo ".gitattributes 已创建并添加视频追踪。"
    fi
else
    echo "注意：未检测到 Git 仓库。建议在初始化后执行 'git init' 并配置 LFS。"
fi

echo "工作区初始化完成。"
