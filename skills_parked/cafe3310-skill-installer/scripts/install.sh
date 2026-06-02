#!/bin/bash

# 辅助函数：让用户从存在的目录中选择，优先非空
choose_base_dir() {
    local label=$1
    shift
    local candidates=("$@")
    
    local existing_non_empty=()
    local existing_empty=()

    # 分类存在的目录
    for dir in "${candidates[@]}"; do
        local expanded_dir="${dir/#\~/$HOME}"
        if [ -d "$expanded_dir" ]; then
            if [ "$(ls -A "$expanded_dir" 2>/dev/null)" ]; then
                existing_non_empty+=("$dir")
            else
                existing_empty+=("$dir")
            fi
        fi
    done

    # 合并后的有效选项（非空在前，空在后）
    local valid_options=("${existing_non_empty[@]}" "${existing_empty[@]}")

    # 检查是否有可用选项
    if [ ${#valid_options[@]} -eq 0 ]; then
        echo "错误：未找到任何有效的候选目录 (${candidates[*]})" >&2
        exit 1
    fi

    echo -e "\033[1;36m请选择 $label 的基础安装目录 (推荐使用非空目录)：\033[0m" >&2
    for i in "${!valid_options[@]}"; do
        local suffix=""
        # 标记非空目录
        for ne in "${existing_non_empty[@]}"; do
            if [ "$ne" == "${valid_options[$i]}" ]; then
                suffix=" (当前非空，优先推荐)"
                break
            fi
        done
        echo "$((i+1))) ${valid_options[$i]}$suffix" >&2
    done

    local default_choice=1
    while true; do
        read -p "选择 (1-${#valid_options[@]}, 默认为 $default_choice): " choice <&2
        [ -z "$choice" ] && choice=$default_choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#valid_options[@]}" ]; then
            local selected="${valid_options[$((choice-1))]}"
            echo "${selected/#\~/$HOME}"
            return 0
        fi
        echo "错误：选择无效。" >&2
    done
}

# 1. 基础配置与路径选择
echo "--- 配置安装路径 ---"
# skills 优先顺序: ~/.agents ~/.claude ~/.gemini
SKILLS_BASE=$(choose_base_dir "Skills" "~/.agents" "~/.claude" "~/.gemini")
TARGET_BASE_DIR="$SKILLS_BASE/skills"

REPO_URL="https://github.com/cafe3310/public-agent-skills.git"
TMP_DIR="/tmp/cafe3310-skills-$(date +%s)"

# 2. 克隆仓库到临时目录
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
