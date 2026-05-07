---
name: release-showcase-manager
description: 全生命周期模型发布演示管理。涵盖从素材收集、开发任务设计到视频录制与模型评价的完整流程。
author: cafe3310
license: Apache-2.0
---

# 技能：release-showcase-manager

## 概述

此技能专门用于管理 AI 模型发布期间的大规模演示（Showcase）项目。它不仅仅是一个视频剪辑工具，而是一个**端到端的工程管理框架**。它引导 Agent 从模型能力研究出发，设计并实施具体的开发任务（如 Web 生成、代码工程、移动端应用等），并在开发过程中同步完成录制、笔记记录和性能评价，最终产出可用于发布的演示素材。

此技能深度集成 `doc-todo-log-loop`，确保在复杂的长期任务中能够随时断点续传，保持上下文一致性。

---

## 工作区结构 (Managed Workspace Structure)

当使用此技能管理一个项目时，该项目的工作区（Workspace）应具备以下结构（可参考 `assets/template_workspace/`）：

*   `docs-and-ref/`: 存放模型技术文档、设计参考、提示词模板等（Input/Output）。
*   `notes/`: 存放开发笔记、模型观察记录、Debug 日志（Output）。
*   `showcases/`: 核心输出目录，每个子目录代表一个独立的演示项目（如 `web-app-gen/`, `mobile-ocr/`）。
*   `video-raw/`: 存放原始录屏素材。
*   `video-clipped/`: 存放经过初步裁剪和加工的成品视频。

**结构一致性约束 (Structural Consistency)**：
`showcases/`, `video-raw/` 与 `video-clipped/` **必须**保持完全一致的内部子目录层级。

*   **以 showcases/ 为基准**：用户通常在开发过程中将所有原始素材（录屏、截图）直接存放在 `showcases/` 对应的项目子目录下。
*   **Agent 的职责**：Agent 应当以 `showcases/` 为基准源，负责将原始素材同步/移动至 `video-raw/`，并将加工后的视频存放至 `video-clipped/`，同时严格维护一致的目录层级。禁止在根目录下直接堆放文件。

工作区必须配置 **Git LFS** 以管理大型视频素材。

---

## 核心工作流 (The Pipeline / Sub-commands)

本技能支持通过以下子命令（Workflows）进行阶段化执行。用户可随时要求：“进入阶段 N” 或 “执行 [子命令名]”。

1.  **[discovery] 发现与收集**: 参见 `workflows/01-discovery-and-collection.md`。收集模型画像与素材。
2.  **[planning] 方案设计**: 参见 `workflows/02-planning-and-design.md`。初始化 `doc-todo-log-loop` 并设计 Scenario。
3.  **[execution] 开发实施**: 参见 `workflows/03-development-and-execution.md`。在 `showcases/` 下进行编码实现。
4.  **[capture] 录制与记录**: 参见 `workflows/04-capture-and-notetaking.md`。录制视频并同步更新 `notes/`。
5.  **[evaluation] 评价与洞察**: 参见 `workflows/05-evaluation-and-insights.md`。产出正式的模型评价报告。
6.  **[finalization] 最终产出**: 参见 `workflows/06-finalization.md`。产出成品视频并归档。
7.  **[packaging] 交付包封装**: 参见 `workflows/07-handover-packaging.md`。封装面向视频剪辑师的素材包。

---

## 依赖技能

*   `doc-todo-log-loop`: 用于全程的任务追踪和状态保存。
*   `showcase-video-processor`: 用于后期的视频精修。
*   `oneshot-website` / `ppt-skill`: 作为开发阶段的高效产出工具。

---

## 最佳实践

*   **持续日志**: 每完成一个开发阶段，必须使用 `doc-todo-log-loop` 更新日志。
*   **LFS 意识**: 在提交视频文件前，确保已正确配置 `.gitattributes`。
*   **多维度记录**: 笔记中不仅要记录“做了什么”，更要记录模型在哪些地方表现出了“惊喜”或“挣扎”。
*   **素材裁剪指示持久化**: 将用户提供的所有素材裁剪指令（时间戳、目标时长、变速比等）完整记录在 `video-clipped/CLIPPING_LOG.md` 中，确保每一段剪辑素材都有据可查、可追溯。
*   **交付资产简化**: 在封装交付包时，主动移除冗长的日期前缀和调试后缀。保持目录名为简洁的 `{model} {id} {name}` 格式。
*   **分镜脚本的灵活性**: 在交付文档中明确告知剪辑师，分镜脚本是基于“逻辑点”的建议，鼓励其在保证叙事闭环的前提下，根据视觉节奏进行二次创作。
*   **交付追溯与更新说明**: 在根目录维护 `HANDOVER_LOG.md` 记录每次产出的目录结构快照。若素材包发生更新，需采用覆盖式替换并配以 `UPDATE_NOTES.md` 说明变更项。
