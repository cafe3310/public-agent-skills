---
title: "08-需求表达与示意图绘制规范 (How to Describe Requirements and Wireframes)"
date created: 2026-10-31 Saturday 23:08
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 核心指导指南，规范如何在需求 Tickets (D40) 中撰写平实描述、按步骤绘制 SVG 示意图、控制详略度及标注未评估参数。
references:
  - "[[SKILL]]"
  - "[[04-ticket-design-and-dependency-graph]]"
---

# 08-需求表达与示意图绘制规范 (How to Describe Requirements and Wireframes)

本指南旨在规范 `aop-product-planner` 范式下需求 Ticket (D40) 的撰写质量，定义“看图讲故事”的图文穿插表达、SVG 矢量示意图风格、宿主与新增功能的视觉标定法，以及需求的详略控制原则。

---

## 1. 需求描述的核心原则

### 1.1 学术研究向语调 (Research-Oriented Tone)
* 遵循 `content-tone-adjuster` 去战役感、去大词规范。
* 严禁使用营销化、激情化或非可验证的描述；开门见山陈述现状痛点、工程原因与拟实现的逻辑机制。

### 1.2 Frontmatter 未评估标记原则
* 在需求设计初始阶段，复杂度指标（`design_cost`, `deploy_cost`, `parallelism`, `internal_complexity` 等）与依赖关系（`depends_on_tickets`）应统一标注为 `未评估`。
* 待项目进入阶段 4/5 评审与成本估算时，再由团队填入定量的工时与依赖项。

---

## 2. “看图讲故事” 图文穿插范式 (Visual Storytelling Pipeline)

需求文档的【用户故事 (User Story)】章节应当采用图文交错、按交互步骤逐步推演的形式。

### 2.1 步骤拆解 SOP
1. 划分步骤。将需求拆解为 2-4 个核心交互步骤（如：`步骤 1: 触发入口` -> `步骤 2: 弹窗与控制面板` -> `步骤 3: 状态确认与响应`）；
2. 每一个步骤小节首先嵌入该步骤对应的 SVG 矢量示意图（`![[...-stepN-....svg]]`），紧随其后编写看图描述与体验规约。

---

## 3. 示意图绘制与视觉标注规范 (Wireframe & Highlight Specifications)

### 3.1 图示核心目标与非设计稿定位

> [!IMPORTANT]
> 图示的唯一目标是直观识别「新增内容」：通过对比宿主上下文与新增组件，使阅读者快速识别本次 Ticket 在既有系统中「加了什么」。
> 示意图不代表任何真实的 UI/UX 视觉设计。实际研发展现、排版与组件细节可能完全不同。

### 3.2 图示物理存储与内嵌
* 存储位置：示意图统一使用 SVG 矢量格式，物理文件生成并保存在所在模块/库的合理目录下。例如，Obsidian 的话应该在 `_attachments/` 目录下（文件名如 `YYYY-MM-DD-d40-0001-step1-entry-wireframe.svg`）；
* Markdown 内嵌：合理使用。例如 Obsidian 的话采用 Obsidian 标准内嵌语法 `![[YYYY-MM-DD-d40-xxxx-stepN-wireframe.svg]]` 呈现。

### 3.3 图示表达范式 (Light Minimal + Blue Glow Highlight)

1. 既有界面 —— 极简/空框化处理：
   * 原有界面仅用于提供位置上下文，可以极大程度略写，甚至直接采用无任何文本内容的空白淡灰色方框代替；
   * 文字与线框使用低对比度浅灰色（`stroke="#cbd5e1"` / `fill="#f8fafc"`），表示既有背景。
2. 拟新增功能区 (New Feature Highlight Panel) —— 醒目高亮与细节完备：
   * 在拟新增功能落地的区域，绘制具有蓝色外发光 (Blue Glow Shadow filter) 的部分 (`stroke="#0088ff"` / `filter="url(#blue-glow)"`)，以体现这是新增内容。
   * 内部功能包含度：与既有界面的略写不同，新增功能内部需相对全地包含控制节点。

---

## 4. 详略得当控制原则 (Level of Detail)

在 AOP 面向切面的架构范式下，拆解出的每一个需求 Ticket 本质上都是**增量式 (Incremental) 的切片描述**，而非事无巨细的完整设计说明书。撰写需求与绘制示意图时，需注重整体流畅性与详略平衡：

* **既有基线保持极简**：对于非本次需求变更的既有系统功能与界面上下文，无需展开冗余描述，在图示与正文中保持极简背景呈现即可。
* **增量入口与功能清晰标定**：重点突出本次切片需求所新增的控制入口、交互触点与核心功能节点，使阅读者能直观识别变化的边界。
* **关键逻辑与状态边界平实阐述**：对新增的核心业务逻辑、主要交互流转以及新旧系统衔接时的关键状态清洗与降级规则，做直接、明确的逻辑陈述，避免陷入微观细节的过度设计。

---

## 5. 标准 Markdown 模版范例片段

```markdown
---
title: "D40-0001-多维模型与代理选择控制组件"
date created: 2026-07-27
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
priority: P0
depends_on_tickets: 未评估
design_cost: 未评估
deploy_cost: 未评估
parallelism: 未评估
internal_complexity: 未评估
external_complexity: 未评估
communication_complexity: 未评估
maintenance_impact: 未评估
background: {需求背景简述}
references:
  - "[[AGENTS]]"
  - "[[D31-关联切面]]"
---

## 1. 需求背景和叙事
* 背景与原因：{描述现实问题与工程痛点}

---

## 2. 和我们的哪些 aop 关联
| 参考/拟建功能细项 | 对齐的 AOP 切面 | 转化为本项目的工程指导 |
| :--- | :--- | :--- |
| {新增点} | [[D31-切面]] | {实施参考} |

---

## 3. 用户故事 (User Story) 与看图讲故事

> [!NOTE]
> 这里的表达都是可能的，并非设计良好的。实际可能有差异。

### 3.1 步骤 1：{触发入口}

![[2026-07-27-d40-0001-step1-entry-wireframe.svg]]

#### 场景看图描述与体验规约：
1. 用户心理与状态：{用户在这一步的目标}
2. 常驻控件设计：{触发入口的位置与形态}

### 3.2 步骤 2：{选择器本体与弹窗卡片}

![[2026-07-27-d40-0001-step2-modal-wireframe.svg]]

#### 场景看图描述与体验规约：
1. 全景弹窗与搜素过滤：{搜索与 Tag Pills 求交集过滤}
2. 状态保留与清洗机制：{参数平滑保留与不兼容停用提示}

---

## 4. 关联文档索引
* 根指导：[[AGENTS]]
```

---

## 6. 关联索引

* 主技能文件：[SKILL.md](../SKILL.md)
* 需求拓扑设计：[04-ticket-design-and-dependency-graph.md](04-ticket-design-and-dependency-graph.md)
* 目录结构规范：[00-typical-directory-structure.md](00-typical-directory-structure.md)
