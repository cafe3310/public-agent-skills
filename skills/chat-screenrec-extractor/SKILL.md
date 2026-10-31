---
name: chat-screenrec-extractor
description: 将群聊滚屏录屏视频切帧、交互式框选配置ROI、本地Apple Vision OCR识别，并通过去重算法与LLM整合输出分群Markdown聊天记录
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - ffmpeg
  - python3
  - swiftc
---

# 技能：群聊录屏记录提取器 (Chat Screenrec Extractor)

## 概述

此技能用于将包含群聊滚屏录屏的一系列视频文件（.mp4 / .mov 等）转化为结构化、分群归档的 Markdown 聊天记录。支持：
1. **交互式 Web 调参与 ROI 标定**：可视化调整切帧采样周期（步长/帧率），并在大图上交互式框选「群聊标题栏」与「聊天消息正文区」ROI，一键保存配置。
2. **高精度本地 OCR**：调用 macOS 原生 Apple Vision 框架，零外部 Python 繁重依赖，快速输出文本与精确像素/归一化坐标。
3. **滚屏时序去重与聚类**：利用群聊滚屏在垂直方向移动的坐标连续性与文本相似度算法，自动剔除重叠帧中的冗余行并完成消息段聚合。
4. **分群独立成文**：根据标题栏识别自动识别群聊切换，输出包含发送人、消息内容、时间戳与系统提示的标准 Markdown 文件。

---

## 核心工作流

### 第一阶段：交互式采样调参与 ROI 框选标定 (Calibration)
1. **启动服务**：调用 `server.py`，传入包含录屏视频的目录：
   ```bash
   python3 <path_to_skill>/scripts/server.py --input-dir /path/to/videos --port 8765
   ```
2. **浏览器标定**：
   - 访问 `http://localhost:8765`。
   - 拖动采样滑块（如 0.5s ~ 1.5s/帧），观察当前视频不同时刻的帧画面。
   - 在主画布上拖拽框选：
     - **Title ROI (红色框)**：锁定顶部群聊名称区域（用于自动识别群名及群切换）。
     - **Body ROI (蓝色框)**：锁定消息展示区域（排除顶部状态栏与底部输入键盘）。
   - 点击 **保存配置 (Save Configuration)**，参数将自动写入目标目录下的 `roi_config.json`。

### 第二阶段：批量切帧与原生 OCR 识别 (Batch OCR)
1. **执行提取与识别**：
   ```bash
   python3 <path_to_skill>/scripts/extract_and_ocr.py --config /path/to/videos/roi_config.json
   ```
2. **处理逻辑与产物存放**：
   - 脚本使用 `ffmpeg` 按配置周期将视频抽帧保存至 `<video_dir>/video-frames/` 目录。
   - 图片命名遵循 **`原始名称-mmssSSS.jpg`**（例如 `recording-0133500.jpg`，精确到毫秒）。
   - 同时调用 macOS 原生 OCR CLI 工具对每帧进行文本识别，并在 `video-frames/` 目录下生成同名的文本文件 **`原始名称-mmssSSS.txt`**，记录时间戳、Title 标题和消息区域识别行，便于人工直接快速对照复核。
   - 汇总数据保存为 `.cache/ocr_results/all_frames_data.json`。

### 第三阶段：滚屏去重与消息聚合 (Dedup & Stitching)
1. **执行去重合并**：
   ```bash
   # 若录屏为向下拉取历史记录（从晚到早），使用 --direction reverse
   python3 <path_to_skill>/scripts/dedup_and_stitch.py --ocr-data /path/to/videos/.cache/ocr_results/all_frames_data.json --output-dir /path/to/videos/output --direction reverse
   ```
2. **处理逻辑**：
   - **群识别**：根据 Title ROI 的文字变化切分 Session，自动过滤主屏列表与瞬态系统横幅。
   - **时间标记提取**：识别日期/时间标签（如 `7/28 09:53`、`8/26 14:20`、`昨天 10:15`）。
   - **时序去重与反转重整**：对于向下滑动录制的视频，自动将时间轴重整为**正序（从早到晚）**，比对多帧垂直位移文本行，过滤滚动产生的冗余重复，拼接跨帧长文本。
   - 生成聚合后的候选消息数据 `intermediate_chats.json`。

### 第四阶段：Agent / 模型循环整理与输出 (Format & Polish)
1. **生成最终 Markdown**：
   - 运行格式化导出脚本，或由 Agent 循环校验并补全上下文（修复 OCR 偶发断行、规范化发送人与气泡归属），按群组输出为独立 Markdown 文件：
     `output/[群聊名称].md`
   ```bash
   python3 <path_to_skill>/scripts/format_markdown.py --input /path/to/output/intermediate_chats.json --output-dir /path/to/output
   ```

---

## 产物格式规范

导出的 Markdown 采用清晰的无序列表/对话块结构：

```markdown
# 群聊记录：项目攻坚讨论组 (12)

> 来源视频：`recording_01.mp4`, `recording_02.mp4`
> 整理时间：2026-09-02 22:45

---

### 2026-08-30

**[14:23] 张三**
大家看一下这版方案，有几个关键要点需要确认。

**[14:25] 李四**
收到了，我正在核对接口定义。
> 引用 @张三：大家看一下这版方案，有几个关键要点需要确认。

> [!NOTE]
> 系统提示：王五 加入了群聊

**[14:28] 王五**
大家好！
```

---

## 最佳实践与注意事项

1. **采样频率选择**：
   - 录屏滑动速度较快时，建议将采样间隔设为 `0.5s ~ 0.8s`；滑动较慢时可设为 `1.0s ~ 1.5s`，以兼顾识别完整性与 OCR 计算耗时。
2. **ROI 框选原则**：
   - **标题栏**：尽量紧贴群名称文字上下边界，避免把返回按钮或右侧菜单图标过量包含进来。
   - **消息正文**：顶部避开导航栏底边，底部务必避开底部输入框和发送按钮，防止静止的输入框文本被误当作重复聊天内容。
3. **环境与依赖**：
   - 依赖系统内置的 `ffmpeg` 与 `/usr/bin/swiftc`（macOS 自带），无需通过 pip 安装大型重量级 OCR 模型。
