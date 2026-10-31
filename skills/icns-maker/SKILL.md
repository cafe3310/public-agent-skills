---
name: icns-maker
description: 将 PNG 图标转换为符合 macOS Big Sur+ 视觉与留白规范的标准 .icns 应用图标，支持单图转换与目录批量处理
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - sips
  - iconutil
  - python3
---

# 技能：icns-maker

## 概述

此技能将 PNG 图标转换为符合 macOS 现代设计规范的 `.icns` 格式。

自 macOS Big Sur 起，系统图标采用了统一的 Squircle（连续圆角矩形）视觉网格。在 1024×1024 像素的画布中，实体主体推荐尺寸约为 **824×824 像素**，四周预留约 100px 的透明外边距（Margin / Padding）。直接将撑满 1024×1024 画布的全出血（Full-bleed）图像压制为 `.icns` 会导致图标在 Dock 和 Finder 中视觉明显膨胀、过大。

本技能通过 macOS 自带的 `sips` 与 `iconutil` 自动进行主体缩放、边缘透明垫补，并生成标准的 10 阶分辨率 `.iconset` 打包为 `.icns`。

**关键词**: macOS 图标, icns, iconset, iconutil, sips, 边距补正, Big Sur, 图标制作

## 何时使用此技能

* 从 Figma、Sketch 或 Icon Composer 导出了全出血的 1024×1024 PNG 图标，需要制作合成 `.icns`。
* 发现现有的 `.icns` 在 macOS Dock 或应用程序列表中比系统自带 App 图标明显大上一圈。
* 需要将包含多套不同尺寸（如 `*-16@1x.png` 到 `*-1024@1x.png`）的导出目录批量打包为各自独立的 `.icns`。

## 工作流程

### 1. 命令行调用

本技能脚本统一放置在 `scripts/` 目录下，提供 Python 原生脚本与 Shell 便捷入口。

#### 单图转换
```bash
# 自动垫回透明留白（主体 824px，外扩回 1024px），在同目录生成 AppIcon.icns
python3 <path_to_skill>/scripts/make_icns.py AppIcon.png

# 指定输出文件路径
python3 <path_to_skill>/scripts/make_icns.py AppIcon.png -o /path/to/output.icns
```

#### 目录批量处理
当指定一个目录时，脚本会自动聚合同组的多分辨率 PNG（如 `prefix-1024@1x.png`, `prefix-512@1x.png` 等），挑选最高分辨率文件作为 Master 进行生成：
```bash
# 批量处理整个导出目录
python3 <path_to_skill>/scripts/make_icns.py ~/Downloads/my-icons/

# 或通过 shell 包装脚本
/bin/bash <path_to_skill>/scripts/run.sh ~/Downloads/my-icons/
```

### 2. 常用参数

* `--subject-size <N>`：主体在 1024 画布中的缩放尺寸，默认 `824`。
* `--full-bleed`：原图若已内嵌留白，开启此参数将不额外添加透明外边距。
* `-b`, `--backup`：若目标 `.icns` 文件已存在，先将其备份到 `backup_fullbleed_icns/` 目录再替换。
* `-v`, `--verbose`：输出每一步处理的详细日志。

### 3. 底层标准与分辨率映射

生成的 `.iconset` 包含 Apple 规范所要求的全套 10 阶资产：
- `icon_16x16.png` (16×16)
- `icon_16x16@2x.png` (32×32)
- `icon_32x32.png` (32×32)
- `icon_32x32@2x.png` (64×64)
- `icon_128x128.png` (128×128)
- `icon_128x128@2x.png` (256×256)
- `icon_256x256.png` (256×256)
- `icon_256x256@2x.png` (512×512)
- `icon_512x512.png` (512×512)
- `icon_512x512@2x.png` (1024×1024)

最终调用 `iconutil -c icns <name>.iconset -o <name>.icns` 完成二进制打包，并自动清理中间 `.iconset` 目录。

## 最佳实践

* **源图要求**：尽量提供 1024×1024 像素、带透明通道（Alpha）的高清 PNG 格式源图。
* **圆角注意**：若源图是带 Squircle 圆角的矩形，请确保背景是透明而非纯白色；如果原图不是圆角，在未做遮罩前补边距仍会保留方角。
* **安全替换**：如果是在既有项目或导出目录中重新压制图标，建议加上 `-b` 参数以保留原始 `.icns` 备份。

## 常见陷阱

* **环境依赖**：依赖 macOS 系统原生自带的 `/usr/bin/sips` 和 `/usr/bin/iconutil`，不支持在 Linux 或 Windows 容器下直接运行。
* **重名冲突**：批量模式下默认以公共前缀命名输出文件（如 `gemini-iOS-Default.icns`）。
