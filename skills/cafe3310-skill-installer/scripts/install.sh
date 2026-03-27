#!/bin/bash

# 配置
REPO_URL="https://github.com/cafe3310/public-agent-skills.git"
TMP_DIR="/tmp/cafe3310-skills-$(date +%s)"
TARGET_BASE_DIR="$HOME/.agents/skills"

# 1. 克隆仓库到临时目录
echo "正在从 GitHub 获取最新的 skills 列表 ($REPO_URL)..."
git clone "$REPO_URL" "$TMP_DIR" --quiet

if [ ! -d "$TMP_DIR/skills" ]; then
    echo "错误：克隆的仓库中未发现 'skills' 目录。"
    rm -rf "$TMP_DIR"
    exit 1
fi

# 2. 处理所有技能
mkdir -p "$TARGET_BASE_DIR"

echo "正在处理并安装技能..."

for skill_path in "$TMP_DIR"/skills/*; do
    if [ -d "$skill_path" ]; then
        skill_name=$(basename "$skill_path")
        target_skill_dir="$TARGET_BASE_DIR/$skill_name"
        
        should_copy=false
        
        if [ -d "$target_skill_dir" ]; then
            # 检查已存在的 SKILL.md 是否属于 cafe3310
            skill_md_path="$target_skill_dir/SKILL.md"
            if [ -f "$skill_md_path" ] && grep -qi "cafe3310" "$skill_md_path"; then
                echo "[更新] 技能 '$skill_name' 是 cafe3310 的，正在自动覆盖更新..."
                should_copy=true
            else
                # 对于非 cafe3310 的技能，输出警告并提示手动处理
                echo "[跳过] 技能 '$skill_name' 已存在但不是由 cafe3310 提供的。为防止意外覆盖，已跳过。请手动确认后再处理。"
                should_copy=false
            fi
        else
            echo "[新安装] 技能 '$skill_name' 正在安装中..."
            should_copy=true
        fi
        
        if [ "$should_copy" = true ]; then
            rm -rf "$target_skill_dir"
            cp -r "$skill_path" "$target_skill_dir"
        fi
    fi
done

# 3. 展示已安装的技能和作用
echo -e "\n----------------------------------------"
echo "✅ 已成功安装/更新以下来自 cafe3310 的技能："
echo "----------------------------------------"
printf "%-35s | %s\n" "技能名称" "功能描述"
printf "%-35s | %s\n" "----------" "-----------"

for skill_dir in "$TARGET_BASE_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        skill_md="$skill_dir/SKILL.md"
        if [ -f "$skill_md" ]; then
            # 提取第一个标题或描述行
            description=$(grep -m 1 "^#" "$skill_md" | sed 's/^#* //')
            [ -z "$description" ] && description="暂无描述。"
            printf "%-35s | %s\n" "$skill_name" "$description"
        fi
    fi
done

# 清理
rm -rf "$TMP_DIR"
echo -e "\n🎉 所有技能已就绪，您可以让 Agent 开始工作了！"
