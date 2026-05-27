---
name: interview-processor
description: 处理面试记录的 Agent 技能。包含面试大纲规划、面试提问提取与纠错、面试总结自评，以及知识图谱存储方案。
author: github/cafe3310
license: Apache-2.0
depends_on_skill:
  - github/cafe3310/agent-skill-memories-off -> memories-off
depends_on_binary: []
---

# Agent Skill: interview-processor (面试记录处理技能)

本技能用于辅助面试官在面试前后进行高效的结构化处理，沉淀招聘成果并客观自评提问水平。它可以配合 `memories-off` 技能的 `memocli` 将生成数据安全写入本地知识图谱。

## 1. 依赖工具 (Dependencies)

本技能依赖本地优先的知识库管理工具 `memocli`。在执行任何图谱写入前，请确保 `memocli` 已经配置，并知晓知识库根目录的路径（可通过 `--path` 或 `-p` 传入）。

常用 `memocli` 命令参考：
- `memocli explore -p <path>`：全局探索。
- `memocli search-entities <pattern> -p <path>`：模糊检索实体。
- `memocli create-entity -p <path> -e <name> -t <type> -c <content> --add-rel-out <rel>`：创建新实体并建立关系。
- `memocli append-update -p <path> -e <name> -c <content> --add-rel-out <rel>`：以追加更新块模式更新实体。

---

## 2. 动态上下文加载机制 (Interviewer Persona)

为了保证面试总结中“团队介绍”以及对面试官表现的自评贴合面试官当前的最新岗位和团队，本技能采用**知识图谱优先**的动态画像加载机制：

1. **第一步**：在执行任何子任务前，Agent 必须运行：
   ```bash
   memocli search-entities "我自己的面试官画像" -p <path>
   ```
2. **第二步**：
   - 若实体存在，Agent 应读取其正文（通常包含 `## 当前岗位与团队` 和 `## 个人面试偏好`），以其内容作为当前的背景上下文。
   - 若实体不存在，Agent 应友好提醒面试官，并引导其使用以下命令初始化该画像：
     ```bash
     echo "## 当前岗位与团队
     [在此写明您当前的岗位、所负责团队及核心业务介绍]
     
     ## 个人面试偏好
     [在此写明您的面试风格、提问原则和关注特质]" | memocli create-entity -p <path> -e "我自己的面试官画像" -t "个人画像" --content-stdin --reason "初始化面试官个人画像"
     ```

---

## 3. 数据实体建模方案 (KG Entity Models)

本技能在本地知识库中管理四类实体。为符合 `memories-off` 规范，所有实体必须遵循严格的 H1 (`# 实体名`) 与 H2 (`## 章节名`) 标题层级，禁止使用 H3 及以下标题。

### 3.1 个人画像 (Interviewer Persona)
- **命名规范**：`我自己的面试官画像`
- **实体类型 (type)**：`个人画像`
- **核心章节**：
  - `## 当前岗位与团队`
  - `## 个人面试偏好`

### 3.2 面试方法论 (Interview Methodology)
- **命名规范**：`[领域/岗位]专家面试风格-YYYYMMDD` （例如：`iOS专家面试风格-20250718`）
- **实体类型 (type)**：`面试方法论`
- **核心章节**：
  - `## 面试风格与偏好`（列出面试官在该领域的提问原则、风格和追问逻辑）

### 3.3 面试问题集 (Interview Question Set)
- **命名规范**：`[领域/岗位]面试问题集-YYYYMMDD` （例如：`大模型产品面试问题集-20250729`）
- **实体类型 (type)**：`面试问题集`
- **核心章节**：根据面试的方向或技术模块划分的多个 H2 章节。
  - `## 核心认知与边界理解`
  - `## 系统设计与成本控制`
  - ... (根据实际方向动态创建)
- **出站关系**：
  - `target_methodology` 指向其对应的 `[领域/岗位]专家面试风格-YYYYMMDD` 实体。

### 3.4 面试记录 (Interview Record)
- **命名规范**：`对[候选人姓名]的面试总结 (YYYY-MM-DD)`
- **实体类型 (type)**：`面试记录`
- **核心章节**：
  - `## 基本信息`（候选人姓名、招聘类型 [校招/社招/数字马力]、岗位名称、面试日期）
  - `## 面试反馈`（建议层级、优势、不足、结论）
  - `## 沟通记录与评价`（核心讨论话题列表与候选人回答情况评估）
  - `## 面试官表现自评`（以专家级别对面试官提问、追问、得体度做出的客观改进要求）
- **出站关系**：
  - `use_style` 指向对应 `面试方法论` 实体。
  - `use_question_set` 指向对应 `面试问题集` 实体。
  - `candidate` 指向候选人个人实体（若有）。

---

## 4. 子任务导航 (Subtasks Navigator)

当用户触发本技能时，请根据当前所处的面试阶段，跳转至对应的子任务执行详细指南：

*   **面试前**：[子任务 1：规划面试大纲](file:///Users/sipan/workspace/_working/public-agent-skills/skills/interview-processor/task-1-pre-interview.md) —— 结合简历、JD 生成定制化面试大纲。
*   **面试后 (提问整理)**：[子任务 3：整理真实提问](file:///Users/sipan/workspace/_working/public-agent-skills/skills/interview-processor/task-3-post-interview-questions.md) —— 从录音转写中提炼、纠错、规范化面试官的所有真实提问。
*   **面试后 (纪要总结)**：[子任务 2：整理面试纪要与评估](file:///Users/sipan/workspace/_working/public-agent-skills/skills/interview-processor/task-2-post-interview-summary.md) —— 生成面试总结报告、进行专家级面试官表现自评，并写入知识图谱。
