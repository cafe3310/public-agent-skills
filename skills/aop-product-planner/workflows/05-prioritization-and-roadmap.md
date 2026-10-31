---
title: "05-优先级排列与交付 Roadmap 规范 (Phase 5: Prioritization & Roadmap)"
date created: 2026-10-31 Saturday 23:20
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 阶段五工作流规范，定义如何基于用户显式提供的优先级决策输入，结合系统依赖评估 P0/P1/P2 并输出交付 Roadmap。
references:
  - "[[SKILL]]"
  - "[[04-ticket-design-and-dependency-graph]]"
---

# 阶段五：优先级排列与交付 Roadmap 规范 (Phase 5: Prioritization & Roadmap)

## 1. 阶段目标与用户决策法则

阶段五的目的是**结合系统依赖、团队资源与用户显式提供的决策输入，对需求 Ticket 进行分级标注，输出可落地的交付里程碑图谱 (Roadmap)**。

在此阶段，必须严格遵守以下决策法则：

### 核心法则：优先级的决策输入必须由用户显式提供 (User-Driven Priority Inputs)

由于每个项目、产品与团队在不同阶段的业务目标、资源情况与风险偏好不同，**优先级的判定绝不能依赖 Agent 单方面决定**。

在评估优先级时， Agent 与用户的职责边界如下：
1. **Agent 的职责**：梳理并呈现在阶段四（`D40`）中拆解的所有需求 Ticket 及其前后置依赖 DAG 图谱；引导并询问用户的优先级决策偏好。
2. **用户的职责**：向 Agent 显式提供优先级的决策输入（例如指定“优先实现核心流程”、“优先接入外部接口”或“优先完成特定关键切面”）。
3. **Agent 依据用户输入执行**：在收到用户的明确优先级指导后，Agent 按照规范标注 P0 / P1 / P2 属性，并格式化排定里程碑 Roadmap。

---

## 2. 优先级分级标准定义 (仅供用户决策参考)

在向用户征集决策输入时，可提供以下客观标准供用户参考：

* **P0 级 (Core MVP & Essential Infrastructure)**：
  * **定义**：用户指定的构成系统基础体验的核心设施，或解决核心问题、高频使用的关键功能。
* **P1 级 (Value Add & Operations Supply)**：
  * **定义**：丰富前台展示、提高宣发效率、支持二方/合作伙伴集成或提供反馈排查的次高优先级功能。
* **P2 级 (Advanced Enhancement & Scalability)**：
  * **定义**：高阶拓展、长尾优化或后置的自动化演进功能。

---

## 3. 标准操作流程 (SOP)

### 步骤 1：呈现需求列表与依赖拓扑 (Present Tickets & Dependencies)
* 向用户展示阶段四梳理的 `D40` 需求 Ticket 清单及其依赖关系。

### 步骤 2：征集用户优先级决策输入 (Collect User Inputs)
* 主动询问用户对于本次交付的优先级偏好（如当前阶段的关注重点、关键里程碑要求）。

### 步骤 3：依据用户输入进行 Ticket 标注 (Tagging)
* 依据用户的明确答复，在需求列表中为每一个 Ticket 标注 P0 / P1 / P2 属性及判定理由。

### 步骤 4：交付里程碑图谱生成 (Milestone Mapping)
* 按里程碑分类归集需求，生成完整的系统交付 Roadmap 矩阵表。

---

## 4. 阶段产出物与目录约定

本阶段产生的交付物及其在项目目录中的存储位置，统一遵循：
👉 **[00-typical-directory-structure.md](00-typical-directory-structure.md)**（主要落地在 `D20-目标与重点/` 与 `D40-需求列表/` 的优先级标记项）

---

## 5. 关联索引

* **主技能文件**：[SKILL.md](../SKILL.md)
* **需求依赖**：[04-ticket-design-and-dependency-graph.md](04-ticket-design-and-dependency-graph.md)
