# 工作流 02：初稿素材加工 (Draft Video Processing)

## 目的
使用 FFmpeg 对原始素材进行“清洗”和“标准化”，产出高质量、节奏紧凑的初稿素材（First Draft Assets）。

## 输入
*   经过工作流 01 整理后的素材文件及其对应的 `.txt` 侧边文档（包含编辑意图）。

## 步骤

### 1. 意图解析
*   读取 `.txt` 文件中的 `--- 编辑意图 ---` 部分。
*   解析 `Crop`, `Trim`, `Speed`, `Freeze/Zoom` 等参数。

### 2. FFmpeg 指令生成
针对不同操作，构建高质量指令：

*   **裁剪 (Crop)**:
    `ffmpeg -i in.mp4 -vf "crop=w:h:x:y" -c:v libx264 -crf 18 -preset slow out.mp4`
*   **修剪 (Trim)**:
    `ffmpeg -i in.mp4 -ss [start] -to [end] -c:v copy out.mp4` (尽量使用 copy 以保持无损)
*   **智能变速 (Time Warp)**:
    对特定时间段应用 `setpts` 滤镜，例如加速 4x: `0.25*PTS`。
*   **定格 (Freeze)**:
    提取特定帧并转换为短视频，再与原视频拼接。

### 3. 质量控制
*   **分辨率**: 默认保持原始分辨率，或统一提升至 4K（使用高质量 Upscaler）。
*   **色彩空间**: 保持或转换为 `yuv420p` 以确保全平台兼容性。
*   **码率**: 始终使用高质量设置（CRF 18 或更高）。

### 4. 批处理执行
*   按顺序执行生成的所有 FFmpeg 指令。
*   将处理后的素材存入 `draft_assets/` 目录。

## 输出
*   一组干净、紧凑、符合预期的初稿视频文件。
*   每个文件已去除多余 UI，且节奏经过优化。
