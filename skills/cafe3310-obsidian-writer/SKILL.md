---
name: cafe3310-obsidian-writer
description: 编写符合 cafe3310 的 Obsidian 仓库风格的文档。
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary: []
---

# cafe3310-obsidian-writer

本技能指导 Agent 如何编写与 cafe3310 知识库风格高度统一的文档。

## 1. 命名与符号

- **命名格式**：`YYYY-MM-DD-HH-mm-标题` 或 `YYYY-MM-DD 📅️ 标题`。
- **Emoji 语意**：
    - `🟥`：待办/未完成/待编写。
    - `🟩`：已完成/已提供。
    - `📅️`：定期摘要（日报、周报）。

## 2. 结构与溯源

所有文档**必须**包含：
1. **YAML Frontmatter**：包含 `title`, `date created`, `date modified`。
2. **标签行**：紧随 YAML 之后，包含 `#Type-` 和 `#Project-` 标签。
3. **01. 文档生成说明**：明确记录 Agent 生成原因及参考文档（使用 `[[双向引用]]`）。

## 3. 文风指南

- **资深工程师风格**：高信息密度，拒绝冗余。
- **结构化优先**：使用列表、引用块和任务项。
- **强链接**：通过双向链接建立知识网络。

## 4. 参考资源

- 详细标签与符号定义见：[categories.md](references/categories.md)
- 标准文档模板见：[template.md](assets/template.md)
