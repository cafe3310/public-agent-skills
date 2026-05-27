---
name: gemini-omni-video-to-sticker-gif
description: 此技能用于提取视频片段并制作微信等平台的高质量动态表情包 (GIF)。支持截取带刻度网格的预览帧以精确定位坐标，并支持裁剪、缩放、速度调整以及最后一帧定格等高级参数设置。
license: Apache-2.0
author: github/antigravity
depends_on_skill: []
depends_on_binary:
  - ffmpeg
  - ffprobe
  - python3
---

# 技能：gemini-omni-video-to-sticker-gif

## 概述

此技能专门用于将任意视频（如 MP4）转换为高品质的 GIF 动态表情包。在制作微信表情包等场景下，它提供了从“坐标校准”到“动图生成”的完整工作流。支持在截图中绘制红黄相间的像素坐标刻度（精确到 50px），帮助用户精确确定裁剪范围。

**关键词**: 视频转GIF, 微信表情包, 坐标定位, GIF加速, 帧定格, ffmpeg

## 何时使用此技能

* 当您想将一段视频转换成 GIF 表情包，但不确定具体的裁剪坐标时。
* 当您需要精确定位视频中某个主体的坐标，想生成一张带有像素尺度的预览图时。
* 当您需要调整 GIF 速度（如 1.5 倍速），或者想让 GIF 最后一帧定格一段时间（如定格 0.4 秒）时。

## 目录结构

```
gemini-omni-video-to-sticker-gif/
├── SKILL.md
└── scripts/
    └── video_to_gif.py   # 核心处理脚本
```

## 参数说明

脚本 `video_to_gif.py` 接收以下参数：

* `video_path` (位置参数): 输入视频文件的绝对路径。
* `-o`, `--output`: 输出 file 路径。如果是 `--grid` 模式，输出为 PNG 预览图；否则输出为 GIF 动图。
* `--ss`: 截取起始时间（例如 `2.5`，单位为秒，默认为 `0.0`）。
* `-t`, `--duration`: 截取的时长（例如 `3.5`，单位为秒）。
* `--to`: 截取的结束时间（例如 `6.0`，单位为秒）。如果提供了 `--to`，会自动计算时长 `duration = to - ss`。
* `--crop`: 裁剪区域。支持以下两种格式：
  - `w:h:x:y` (FFmpeg 标准格式，如 `700:700:292:10`)
  - `x,y,w,h` (如 `292,10,700,700` 或 `xy292x10 wh700x700` 格式)
* `--scale`: 输出尺寸（例如 `600:600`，默认为 `600:600`）。
* `--speed`: 播放速度倍数（例如 `1.5`，默认为 `1.0`，大于 1.0 为加速，小于 1.0 为减速）。
* `--freeze`: 最后一帧定格时长（例如 `0.4`，单位为秒，默认为 `0.0`，即不定格）。
* `--grid`: 启用网格模式。开启后不会生成 GIF，而是提取 `--ss` 时间点的一帧，并在其上叠加像素坐标刻度（红线代表 100px，黄虚线代表 50px），用于精确定位。

## 使用示例

### 1. 提取并生成带刻度的坐标参考图
如果您不确定坐标，先生成一张带有坐标网格 of 预览帧（第 2.0s 处）：
```bash
python3 <path_to_skill>/scripts/video_to_gif.py /path/to/video.mp4 --ss 2.0 --grid -o /path/to/preview_grid.png
```

### 2. 生成 1.5 倍速、无定格的表情包
根据预览图确定的坐标 `x=352, y=39, w=630, h=630`，截取 `2.5s - 6.0s` 视频段，制作 1.5 倍速表情包：
```bash
python3 <path_to_skill>/scripts/video_to_gif.py /path/to/video.mp4 --ss 2.5 --to 6.0 --crop 630:630:352:39 --speed 1.5 -o /path/to/output.gif
```

### 3. 生成 1.2 倍速、最后一帧定格 0.4 秒的表情包
```bash
python3 <path_to_skill>/scripts/video_to_gif.py /path/to/video.mp4 --ss 2.2 --to 6.2 --crop 700:700:319:10 --speed 1.2 --freeze 0.4 -o /path/to/output_freeze.gif
```

## 常见陷阱与注意事项

1. **依赖项**: 系统必须安装有 `ffmpeg` 和 `ffprobe`，并已加入环境变量。
2. **裁剪区域越界**: 填写的 `x + w` 或 `y + h` 不能超出视频原始的分辨率，否则 ffmpeg 会报错。可以使用 `ffprobe` 先查看视频原始分辨率，或直接参考生成的 `--grid` 图像的边缘刻度。
3. **微信表情包大小限制**: 微信自定义表情大小限制通常为 5MB（有些老版本限制更低）。如果生成的 GIF 太大，建议通过减小时长、调低帧率或缩放尺寸（例如从 600x600 缩小到 300x300）来控制文件大小。
