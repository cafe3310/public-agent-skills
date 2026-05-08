# Agent Instructions

此工作区由 `release-showcase-manager` 技能管理。

## 核心依赖技能

在该工作区进行任务时，必须激活并遵循以下技能：

- **`release-showcase-manager`**: 负责全生命周期的演示项目管理、目录规范及视频处理工作流。
- **`doc-todo-log-loop`**: 负责任务追踪、状态持久化及断点续传。

## 操作指南

1. **初始化/同步**: 确保遵循 `release-showcase-manager` 定义的目录结构。
    - **文档规范**：`notes/` 下的所有文档必须遵循 `yyyy-mm-dd-hh 类型 名字.md` 格式。
    - **目录镜像原则**：`showcases/`, `video-raw/` 和 `video-clipped/` 必须保持完全一致的子目录层级。
    - **同步约定**：Agent 必须以 `showcases/` 目录为基准源。用户录制的原始素材默认存放于 `showcases/`，Agent 负责将其同步至 `video-raw/` 并将剪辑产物存放于 `video-clipped/`，确保资产在不同阶段的可追溯性。
2. **任务驱动**: 所有行动必须记录在 `doc-todo-log-loop` 的日志中。
3. **模型观察**: 在开发过程中，及时将对模型能力的观察记录至 `notes/`。
