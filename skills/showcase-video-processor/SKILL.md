---
name: showcase-video-processor
description: 专门用于模型发布视频的处理。支持原始素材整理、基于 FFmpeg 的初稿编辑（裁剪、变速、缩放等）以及多粒度分镜文档策划。
license: Apache-2.0
status: wip
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - ffmpeg
---
---

# 技能：showcase-video-processor

## 概述

此技能旨在协助模型团队（AI Model Teams）高效制作高质量的发布演示视频（Showcase Videos）。它通过标准化的 Pipeline，将原始的代码、提示词、截图和录屏素材转化为符合“Luxury Tech”审美的初稿素材，并最终组织成完整的演示集（Showcase Set）。

**关键词**: 视频处理, FFmpeg, 模型演示, 分镜策划, 素材整理

---

## 核心功能

### 1. 原始素材整理 (Asset Organization)
*   **重命名**: 遵循 `{YYYYMMDD}_{类型}_{描述}_{序号}.{后缀}` 规范。
*   **侧边文档**: 为每个素材自动创建同名的 `.txt` 说明文件，记录原始参数、录制背景及编辑意图。

### 2. 初稿视频编辑 (Draft Video Processing)
基于 FFmpeg 的无损/高质量处理，包含：
*   **裁剪 (Crop)**: 去除系统 UI（Dock, Menu Bar）。
*   **修剪 (Trim)**: 精确移除开头结尾的冗余。
*   **智能变速 (Time Warp)**: 加速推理过程，保持结果展示正常语速。
*   **缩放与定格 (Zoom & Freeze)**: 关键帧特写与视觉停留。
*   **质量保障**: 最大程度保持原始分辨率与码率，避免二次编码导致的模糊。
*   **[实战案例参考]**: 参见 `concepts/raw_assets_processing.md` 中的 `FFmpeg 综合滤镜处理 (Crop + Partial Speedup)`。

### 3. 多粒度分镜策划 (Storyboard Planning)
根据 `concepts/` 目录下的设计语言，撰写不同层级的文档：
*   **微观分镜**: 针对 `Single Case` 的 4 步走细节。
*   **中观分镜**: 针对 `Collage` 或 `Split Screen` 的布局与节奏。
*   **宏观分镜**: 针对 `Showcase Set` 的完整叙事结构（核心宣告 -> 能力 -> 指标 -> 商业）。
*   **[实战分镜范例]**: 参见 `references/example_releasing_model_max_storyboard.md` 以获取一个完整的、高度执行化（精确到秒与动作）的多模块发布视频分镜参考。

---

## 工作流 (The Pipeline)

### 第一阶段：素材入库 (Ingestion)
1.  用户提供素材目录。
2.  Agent 扫描并重命名文件，生成说明文档。
3.  用户在说明文档中补充细节（如“此处需 4x 加速”）。

### 第二阶段：加工初稿 (Drafting)
1.  Agent 根据说明文档或用户指令生成 FFmpeg 处理命令。
2.  执行处理，产出清晰、紧凑的“初稿视频素材”。
3.  验证处理结果（分辨率、时长、关键内容保留）。

### 第三阶段：分镜与合成 (Compositing)
1.  基于初稿素材，策划分镜文档。
2.  根据选定的模式（单一案例、拼贴、分屏、对比）提出合成建议。
3.  最终整合为发布用的演示集。

---

## 最佳实践
*   **画质优先**: 在所有 FFmpeg 操作中显式指定高质量编码参数（如 `crf 18` 或 `prores`）。
*   **节奏感**: 输出结果展示（Output）严禁加速，给予观众充分评估时间。
*   **Luxury Tech**: 所有的标注、边框和转场应遵循极简、高级的视觉规范。

---

## 常见陷阱
*   **过度裁剪**: 裁剪时需预留一定边距，防止在不同比例屏幕上显示不全。
*   **编码损失**: 避免频繁的格式转换。
*   **信息冗余**: 分镜文档应聚焦于“为何这样展示”，而非单纯记录“做了什么”。
