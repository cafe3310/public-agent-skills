#!/bin/bash

# 此脚本通过一个注重质量的四阶段工作流，处理一个目录中的 PNG 图片，使其适合用作微信表情。

# --- 0. 初始检查与设置 ---


TARGET_DIR=""

# 解析参数
for arg in "$@"; do
  case $arg in

    *) 
      TARGET_DIR="$arg"
      ;;
  esac
done

# 如果命令以非零状态退出，则立即退出。
set -e



if [ -z "$TARGET_DIR" ]; then
  echo "用法: $0 [--debug] <目录路径>"
  echo "错误：请提供包含图片的目录路径。"
  exit 1
fi

if ! command -v magick &> /dev/null; then
    echo "错误：未安装 ImageMagick。请安装后才能使用此技能。"
    exit 1
fi

if ! cd "$TARGET_DIR"; then
    echo "错误：无法切换到目录 '$TARGET_DIR'。"
    exit 1
fi

if [ -z "$(ls -1 *.png 2>/dev/null | head -n 1)" ]; then
  echo "错误：在 '$TARGET_DIR' 中未找到 .png 文件。"
  exit 1
fi

echo "正在创建输出目录..."
rm -rf mid1-bgcolor mid2-trim mid3-border res
mkdir -p mid1-bgcolor mid2-trim mid3-border res

# --- 阶段 1：统一背景颜色 ---
echo "---"
echo "阶段 1：正在处理 -> mid1-bgcolor"

# ... (颜色计算逻辑的其余部分保持不变)
INFO_FILE="mid1-bgcolor/info.txt"
echo "颜色采样日志" > "$INFO_FILE"
ALL_COLORS=""
echo "正在从每张图片的 4 个角采样颜色..."
for file in *.png; do
  if [ -f "$file" ]; then
    SAMPLED_COLORS=$(magick "$file" -format '%[pixel:p{5,5}]\n%[pixel:p{10,5}]\n%[pixel:p{w-5,5}]\n%[pixel:p{w-10,5}]' info:)

    echo -e "\n文件: $file" >> "$INFO_FILE"
echo "$SAMPLED_COLORS" >> "$INFO_FILE"
ALL_COLORS+="$SAMPLED_COLORS\n"
  fi
done
AVG_COLOR=$(echo -e "$ALL_COLORS" | awk '
    BEGIN { sum_r=0; sum_g=0; sum_b=0; count=0; }
    /srgb/ {
        gsub(/srgba?\(|\)|,/, " ");
        sum_r += $1; sum_g += $2; sum_b += $3; count++;
    }
    END {
        if (count > 0) { printf "srgb(%d,%d,%d)", sum_r/count, sum_g/count, sum_b/count; }
        else { print "srgb(255,255,255)"; }
    }
')
echo "确定的平均背景颜色为: $AVG_COLOR"
echo "正在应用统一的背景颜色..."
for file in *.png; do
  if [ -f "$file" ]; then
    echo "  - $file -> mid1-bgcolor/$file"
    CURRENT_TOP_LEFT_COLOR=$(magick "$file" -format '%[pixel:p{0,0}]' info:)
    magick "$file" -fuzz 3% -fill "$AVG_COLOR" -opaque "$CURRENT_TOP_LEFT_COLOR" "mid1-bgcolor/$file"
  fi
done

# --- 阶段 2：裁剪空白 ---
echo "---"
echo "阶段 2：正在处理 -> mid2-trim"
for file in mid1-bgcolor/*.png; do
  if [ -f "$file" ]; then
    BASENAME=$(basename "$file")
    echo "  - $BASENAME -> mid2-trim/$BASENAME"

    magick "$file" -fuzz 5% -trim +repage "mid2-trim/$BASENAME"
  fi
done

# --- 阶段 3：添加内边距并创建方形画布 ---
echo "---"
echo "阶段 3：正在处理 -> mid3-border"
for file in mid2-trim/*.png; do
  if [ -f "$file" ]; then
    BASENAME=$(basename "$file")
    echo "  - $BASENAME -> mid3-border/$BASENAME"
    

    DIMENSIONS=$(magick "$file" -format "%w %h" info: || echo "0 0")
    read -r W H <<< "$DIMENSIONS"


    if [ -z "$W" ] || [ "$W" -eq 0 ]; then
    
        # 如果裁剪失败，我们从阶段 1 复制未经裁剪的版本
        cp "mid1-bgcolor/$BASENAME" "mid3-border/$BASENAME"
    else
        H_PADDED=$(awk -v h="$H" 'BEGIN { print int(h * 1.04) }')
    

        SQUARE_SIZE=$(awk -v w="$W" -v h="$H_PADDED" 'BEGIN { print (w > h ? w : h) }')
    

        # 在此逻辑中，我们使用 mid2-trim 中已经裁剪过的文件
        magick "$file" -background "$AVG_COLOR" -gravity Center -extent "${W}x${H_PADDED}" png:- | \
          magick - -background "$AVG_COLOR" -gravity Center -extent "${SQUARE_SIZE}x${SQUARE_SIZE}" "mid3-border/$BASENAME"
    fi
  fi
done

# --- 交互式暂停 ---
echo
echo "⏸️  暂停：阶段 3（添加边框）已完成。"
echo "您现在可以检查 'mid3-border' 目录中的图片。"
echo "如果您想进行手动调整，请现在进行。"
read -p "按 [Enter] 键继续进行阶段 4（最终调整大小）..."
echo

# --- 阶段 4：最终调整大小 ---
echo "---"
echo "阶段 4：正在处理 -> res"
for file in mid3-border/*.png; do
  if [ -f "$file" ]; then
    BASENAME=$(basename "$file")
    echo "  - 正在调整 $BASENAME -> res/$BASENAME"
    magick "$file" -filter LanczosSharp -resize 240x240 -background "$AVG_COLOR" -gravity center -extent 240x240 "res/$BASENAME"
  fi
done

echo "---"
echo "✅ 技能 'wx-emoji-maker' 已成功完成。"
echo "最终图片位于 'res' 目录中。"
echo "中间文件位于 'mid1-bgcolor'、'mid2-trim' 和 'mid3-border' 中。"
echo "颜色分析报告位于 'mid1-bgcolor/info.txt'。"