# Phase 4: 录制与记录 (Capture & Notetaking)

## 目标
执行高质量录制，通过结构化标签文件定义剪辑意图，并调用 `showcase-video-processor` 产出成品。

## 1. 录制执行与命名 (Execution & Naming)

按照 Phase 3 准备的环境进行录制。
- **原始素材存放**: `video-raw/` 目录下。
- **命名规范**: `{YYYY-MM-DD-HH}-{model}-{desc}-raw.{ext}`。
- **Git LFS**: 确保视频文件被 Git LFS 追踪。

## 2. 结构化标注文件 (Sidecar Labeling)

为每个原始视频创建一个同名的 `.txt` 标注文件（例如 `...-raw.txt`），用于定义剪辑逻辑。

**标注格式**:
`[开始时间] - [结束时间] | [动作/Action] | [说明/Description]`

**支持的动作**:
- **Normal**: 原速展示。
- **Zoom [倍率]**: 局部放大（如 `Zoom 1.5x`），需在说明中注明焦点。
- **Speed [倍数]**: 加速处理（如 `Speed 4x`），用于跳过等待环节。
- **Trim**: 丢弃该段。

**示例内容**:
```text
00:00 - 00:05 | Normal | 开场展示 Prompt。
00:05 - 00:15 | Zoom 1.2x | 聚焦模型生成代码的瞬间。
00:15 - 00:45 | Speed 8x | 自动跳过依赖安装过程。
00:45 - 01:20 | Normal | 最终运行效果演示。
```

## 3. 视频加工手账 (Processing Hand-off)

1. **激活技能**: 激活 `showcase-video-processor`。
2. **指令下达**: 将标注文件交给 Agent，要求其根据标注生成并执行 FFmpeg 指令。
3. **裁剪知识持久化 (Knowledge Persistence)**:
   - **操作**: 将本次用户提供的所有裁剪逻辑（源文件路径、时间戳范围、目标时长、变速倍率）完整记录到 `video-clipped/CLIPPING_LOG.md`。
   - **意义**: 确保后期如果需要重新调整或溯源时，原始的剪辑指示清晰可见。
4. **成品产出**: 
   - **存放路径**: `video-clipped/` 目录下。
   - **命名规范**: `{YYYY-MM-DD-HH}-{model}-{desc}-clipped.mp4`。

## 4. 同步笔记记录 (Final Notetaking)

- 在对应的 `showcases/{dir}/notes.md` 中补充最终录制时的观察。
- 记录模型在“动态演示”中是否表现出与“静态代码”一致的稳定性。

## 完成标准
- [ ] `video-raw/` 下已存放原始素材及对应的结构化标注文件。
- [ ] 已调用 `showcase-video-processor` 产出对应的 `video-clipped/` 成品。
- [ ] 视频命名严格遵循 YYYY-MM-DD-HH 规范。
