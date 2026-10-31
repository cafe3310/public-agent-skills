---
title: "02-AOP切面大网划分规范 (Phase 2: Aspect Network Categorization)"
date created: 2026-10-31 Saturday 23:13
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 阶段二工作流规范，定义如何依据 AOP 关注点分离原则搭建系统切面大网与三层架构。
references:
  - "[[SKILL]]"
---

# 阶段二：AOP 切面大网划分规范 (Phase 2: Aspect Network Categorization)

## 1. 阶段目标与 AOP 切面核心法则

阶段二的目的是**按面向切面关注点 (AOP) 建立系统的全景分类图谱**。

在划分切面时，必须严格贯彻以下两项方法论法则：

### 法则一：三分层架构 (3-Layer Architecture)
* **面向用户与运营交付层 (User & Operations Layer)**：
  前台用户可直接感知、操作调试、使用场景、试用多模态及运营宣发引流的功能集合。
* **开发者、开放接口与二方交付层 (Developer, API & 2nd-Party Layer)**：
  面向开发者、第三方系统与内部二方团队的标准 API 接口、一方 SDK 交付、代码导出与计费配额管控。
* **纯内部基建层 (Internal Infrastructure Layer)**：
  完全隐匿于底层，服务于声明式 spec 模板解析、沙箱隔离环境及数据积累与系统演进的基础设施管道。

### 法则二：功能点跨切面重叠法则 (Overlap Acceptance)
* 评估切面时不追求“功能物理互斥”。一个具体的功能点（如数据缓存、第三方服务集成或指标展示）可以同时归属于多个切面。切面代表的是观察视角的差异，而非硬性排他分区。

---

## 2. 标准操作流程 (SOP)

### 步骤 1：梳理切面分类拓扑 (Aspect Topology Design)
* 从三层架构出发，枚举系统需要覆盖的所有横切关注点。
* 为每个切面分配唯一单级编号（推荐使用 `D30` 系列前缀，如 `D31` 至 `D4x`）。

### 步骤 2：撰写切面总览与子文档 (Aspect Indexing)
* 创建主总览文档（如 `D30-主功能分类与AOP三层架构总览.md`），绘制全景架构树；
* 为每个切面创建独立的研究 Markdown 文档，写入切面定位与初步功能说明。

---

## 3. 阶段产出物与目录约定

本阶段产生的交付物及其在项目目录中的存储位置，统一遵循：
👉 **[00-typical-directory-structure.md](00-typical-directory-structure.md)**（主要落地在 `功能设计/D30-主功能分类(按aop)/`）

---

## 4. 关联索引

* **主技能文件**：[SKILL.md](../SKILL.md)
* **上一阶段**：[01-goal-and-narrative-alignment.md](01-goal-and-narrative-alignment.md)
* **下一阶段**：[03-inbox-harvesting-and-aspect-bounds.md](03-inbox-harvesting-and-aspect-bounds.md)
