---
name: interview-processor
description: 用于处理面试记录的 Agent 技能。输入面试记录(转写)、面试官笔记、岗位信息、简历；输出标准化报告、提问列表、面试官评价与建议，并写入知识图谱。
author: cafe3310
license: Apache-2.0
---

# Agent Skill: interview-processor

处理面试原始记录，并生成结构化面试报告、提问列表以及对面试官的评估与建议，并可选地将其同步至基于 `memories-off` 的本地知识图谱。

## 原始需求关联

- 原始需求文档：[2026-05-27-20-26-original-requirements.md](file:///Users/sipan/workspace/_working/public-agent-skills/skills/interview-processor/2026-05-27-20-26-original-requirements.md)

## 核心输入与输出

### 输入数据 (Inputs)
1. **面试记录** (语音转写文本，通常为非结构化或段落式的对话记录)
2. **面试官笔记** (面试官在面试过程中或面试后记录的简要评价、打分或关键观察)
3. **岗位信息** (岗位描述 JD，包含硬性技能、软性素质要求)
4. **简历** (候选人简历文本)

### 输出数据 (Outputs)
1. **标准化的报告** (结构化面试评估报告，包含候选人亮点、不足、综合评级等)
2. **本次面试官提出的问题** (面试官实际提问的文字整理与分类)
3. **对面试官的评价和优化建议** (针对面试官的提问水平、引导技巧、追问深度的评估和具体改进建议)

---

> [!NOTE]
> 详细的工作流和具体提示词步骤将在用户提供面试提示词后进一步细化并更新至此文档中。
