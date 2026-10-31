---
name: doc-todo-log-loop
description: 该 Skill 已升级并迁移至 /guide skill
license: Apache-2.0
author: github/cafe3310
depends_on_skill:
  - guide
depends_on_binary: []
---

# Skill: doc-todo-log-loop (Deprecated)

> [!IMPORTANT]
> **本 Skill 已全面升级并迁移至 `/guide` Skill。**

## 迁移指引与 Agent 行为要求

1. **能力迁移**：
   - 原有的文档驱动、TODO 循环与规范管理体系已重构升级为 `/guide`（包含 `/guide load`、`/guide spec`、`/guide test`、`/guide log`、`/guide handoff` 等子命令，详见 `skills/guide/SKILL.md`）。

2. **文档更新要求**：
   - 当 Agent 在旧项目配置（如 `AGENTS.md`）、交接文档（如 `HANDOFF.md`）或用户交互中检测到引用了 `doc-todo-log-loop` 时，**应该在提示用户后，在相关文档中将 Skill 名字更新为 `guide`**；
   - 引导用户后续统一使用 `/guide` 体系开展人机协同开发。
