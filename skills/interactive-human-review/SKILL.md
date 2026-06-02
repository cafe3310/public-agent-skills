---
name: interactive-human-review
description: 大范围变更后的互动式人类 review 流程，通过渐进式 checklist 与问答交互确保人类深度理解会话改动
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary: []
---

# Skill: interactive-human-review

## 1. 概述
本 Skill 旨在解决大范围修改后，人类难以完整掌握变更细节和原因的问题；也可用于初次 Review 大量内容时，帮助人类逐步消化和理解。
Agent 将引导用户进行互动式 review，通过渐进式 checklist 与问答反馈，确保用户已经完全掌握全部改动或待 Review 内容。

## 2. 工作流
1. **建立清单**：在修改或讨论之初，在项目或 artifacts 下创建并维护 review 方案文档 `YYYY-MM-DD-HH-mm-review-方案-{简述}.md`（模板见 [Checklist 模板](resources/understanding_checklist_template.md)），作为本次任务的进度跟踪工具。必须在文档建立之初完整探索变更范围或 review 范围，确保范围不遗漏。
2. **渐进式重述**：不推迟到会话结束，每完成一个阶段性修改，主动邀请用户重述其理解，并针对性进行 ELI 级别的查漏补缺（ELI5/ELI14/ELII）。
3. **互动式测验**：基于 Checklist 中的要点，使用 `AskUserQuestion` 工具发起开放式或多选题。
   - *注意*：随机打乱选项，且提交前不可泄露答案。
   - 在必要时，直接展示代码行（例如 `[filename.py:L10-20](file://...)`）或引导用户使用调试器。
4. **全部完成后再退出**：用户完全掌握清单上的所有内容并顺利通过测验前，会话目标不判定为完成（`/goal` 条件）。

## 3. 基本原则
- **深挖 Why**：除了 "What" 和 "How" 之外，多问几个 "Why"。
- **用户先行**：先让用户重述，暴露认知盲区后再针对性解释。
- **保护答案**：在用户回答前，绝不在 Thought 或回复中剧透测验答案。
- **开发项目多维理解**：如果 review 的是代码或开发项目，要留意引导人类理解并掌握**计划（Plan）、设计（Design）、架构（Architecture）、实现（Implementation）、测试（Testing）、用户故事（User Story）**等多维度的变更细节与联系。
