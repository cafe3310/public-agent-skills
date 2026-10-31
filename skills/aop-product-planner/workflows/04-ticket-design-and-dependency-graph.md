---
title: "04-需求列表与依赖拓扑设计规范 (Phase 4: Ticket Design & Dependency Graph)"
date created: 2026-10-31 Saturday 23:18
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 阶段四工作流规范，定义如何将切面功能点细化拆解为需求 Ticket (D40)，并利用 Frontmatter 的 depends_on_tickets 梳理依赖拓扑。
references:
  - "[[SKILL]]"
---

# 阶段四：需求列表与依赖拓扑设计规范 (Phase 4: Ticket Design & Dependency Graph)

## 1. 阶段目标与 Ticket 依赖法则

阶段四的目的是**把切面中的确切功能点细化拆解为可执行的需求卡片 (Tickets)，并建立清晰的强依赖拓扑关系**。

在此阶段，必须遵循以下法则：

1. **Ticket 4 位零填充单级编号与规范归集 (D40 Block)**：
   * 所有具体需求点统一放置在 `D40-需求Tickets/`（或 `D40-需求列表/`）目录下；
   * 采用 `D40-nnnn-简述.md` 4 位零填充递增编号格式（例如 `D40-0001-需求名称.md`），保证在文件管理与知识库中升序对齐。
2. **Frontmatter 强依赖属性 (`depends_on_tickets`)**：
   * 每一个需求 Ticket 的 YAML Frontmatter 中必须包含 `depends_on_tickets` 数组列表；
   * **前置约束规则**：如果需求 $X$ 未完成，则绝对无法开始依赖于它的需求 $Y$。
3. **显式链接 (Linkage)**：
   * 每一个需求 Ticket 必须显式包含 Markdown 链接，如果有：
     * **关联切面**：所属的 AOP 切面文档链接 (`D3x`)；
     * **关联对标分析**：参考与解构的竞品/对标功能文档链接 (`D52-nnnn`)；
     * **关联叙事与目标**：支持的定位叙事 (`D1x`) 与平台目标 (`D2x`) 链接；
     * **前置依赖项 (Dependencies)**：显式标明前置强依赖 (`depends_on_tickets`)。

---

## 2. 标准操作流程 (SOP)

### 步骤 1：需求 Ticket 批量拆解 (Ticket Breakdown)
* 从各个切面的【范围内 (Includes)】章节提炼具体的开发功能点；
* 为每个功能点创建独立的 Ticket Markdown 文件。

### 步骤 2：对标分析与用户描述向需求 Ticket 的转化 (Transpilation)
* 无论是读取具体的对标功能点文件（如 `D52-0001-模型选择与推荐展示.md`），还是接收用户随意的口头交流与头脑风暴，均需将原始输入解耦重构成适合本项目架构规范与调性的需求描述；
* 在 Ticket 的 YAML Frontmatter `references` 列表中挂载对应的对标分析文档链接（如 `"[[D52-0001-模型选择与推荐展示]]"`）。

### 步骤 3：全源输入的 `/roast-me` 强质询规范 (Multi-round /roast-me Inquiries)
在正式撰写并导出 Ticket 前，Agent **必须强制使用 `/roast-me` 展开多轮细粒度询问**。询问包含但不限于以下核心维度（保持合理的抽象度，并根据具体场景灵活扩展）：
1. **实现细节 (Implementation Details)**：交互控件、参数设定与边界条件；
2. **关联切面 (Related AOP Aspects)**：归属的 AOP 切面与架构映射（在 YAML 的 `related_aspects` 数组挂载）；
3. **未来特性关联 (Future Functionality)**：后续高级特性与演进接口的预留；
4. **已有需求互动 (Interaction with Past Tickets)**：与此前已建 `D40-xxxx` 需求的状态保留与交互联动；
5. **风险与降级 (Risks & Fallbacks)**：安全隐患、性能上限与底层能力缺失时的降级策略；
6. **场景拓展维度 (Extensible Dimensions)**：根据具体业务与工程场景灵活补充的其他维度。

### 步骤 4：使用标准模版与图文表达范式 (Template & Visual Storytelling)
* 需求 Ticket 的撰写结构、Frontmatter 初始标记及图文表达范式，统一遵循以下规范：
  * **开箱即用模版**：👉 **[D40-ticket-template.md](../templates/D40-ticket-template.md)**
  * **撰写与图示指南**：👉 **[08-how-to-describe-requirements-and-wireframes.md](../references/08-how-to-describe-requirements-and-wireframes.md)**

### 步骤 5：绘制依赖拓扑矩阵 (Dependency Graph)
* 创建 `D40-0000-需求总览与依赖图谱.md`；
* 使用 Mermaid 或结构化列表绘制核心需求间的前后置依赖 DAG 图谱。

---

## 3. 产出交付物标准结构

本阶段产生的交付物及其在项目目录中的存储位置，统一遵循：
👉 **[00-typical-directory-structure.md](../references/00-typical-directory-structure.md)**（主要存储在 `功能设计/D40-需求列表/`）

---

## 4. 关联索引

* **主技能文件**：[SKILL.md](../SKILL.md)
* **上一阶段**：[03-inbox-harvesting-and-aspect-bounds.md](03-inbox-harvesting-and-aspect-bounds.md)
* **下一阶段**：[05-prioritization-and-roadmap.md](05-prioritization-and-roadmap.md)
