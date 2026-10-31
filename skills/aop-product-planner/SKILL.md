---
name: aop-product-planner
description: 面向切面 (AOP) 的智能产品策划与需求拆解范式。用于从目标叙事、AOP 切面分层、乱序 Idea 收集、功能边界界定到需求依赖拓扑与优先级的全流程产品工程规划。
license: Apache-2.0
author: github/cafe3310
depends_on_skill:
  - content-tone-adjuster
depends_on_binary: []
---

# aop-product-planner (面向切面的产品策划与需求架构器)

## 技能描述

本技能提供了一套结构化、泛化、可复用的产品工程策划与需求整理范式。适用于复杂系统、软件产品及数字化平台的平台级架构策划与需求拆解。

核心解决产品设计中“目标模糊、功能混杂、大词滥用、依赖不清”的常见问题。通过**“目标叙事 -> AOP 切面划分 -> Idea 归流与边界确定 -> 需求 Tickets 与依赖拓扑 -> 优先级 Roadmap”**的 5 个阶段流程，将模糊的想法演进为明确的研发实施方案。

---

## 依赖技能

* **`content-tone-adjuster`**：本技能强制依赖 `content-tone-adjuster`（选择学术研究风/去大词模式），以确保在策划全流程中彻底剔除营销化口号与夸张修辞，保持朴素、中立、客观的研究向语气。

---

## 📅 工作流使用时机与项目生命周期 (When to Use)

本技能的 5 个工作流（Workflow）按照项目的不同发展阶段与生命周期节奏执行：

```
                    SKILL: aop-product-planner 工作流 (7 阶段架构)
┌─────────────────────────────────────────────────────────────────┐
│ 1. 大型规划初期 (Initial Project Planning Phase)                 │
│    执行：阶段 1 (目标叙事) -> 阶段 2 (切面大网)                  │
│    目标：先对齐项目底层原则、平实叙事与三层 AOP 切面架构拓扑         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼ (在 阶段1 和 阶段2 达成初步共识后)
┌─────────────────────────────────────────────────────────────────┐
│ 2. 持续迭代与需求开发期 (Continuous Loop Iteration Phase)       │
│    持续、反复、Loop 式地循环执行：                              │
│    ┌──────────────────────────────────────────────────────┐     │
│    │ 阶段 3 (Idea吸收与边界确定)                          │     │
│    │    └─► 阶段 4 (需求列表与依赖拓扑设计)                │     │
│    │         └─► 阶段 5 (基于用户输入的优先级与 Roadmap)    │     │
│    │              └─► 阶段 6 (6维复杂度与周期成本建模)     │     │
│    │                   └─► 阶段 7 (网页预览与勾选计算器)  │     │
│    │                        └─► (反复 Loop 回到阶段 3)    │     │
│    └──────────────────────────────────────────────────────┘     │
│    目标：持续吸收想法，确定界限，评估 6 维复杂度并编译网页面板   │
└─────────────────────────────────────────────────────────────────┘
```

### 具体阶段触发时机说明：

* **阶段 1：目标与叙事定义 (Goal & Narrative Alignment)**
  * **何时使用**：项目/大规划立项极早期。
  * **作用**：设立核心评估准则（杜绝数据刷分），撰写平实客观的故事背景与定位分析，统一去大词语调。
* **阶段 2：AOP 切面大网划分 (Aspect Network Categorization)**
  * **何时使用**：项目/大规划立项极早期（紧跟阶段 1）。
  * **作用**：搭建系统的 AOP 切面大网（三分层架构），确立“功能点允许跨切面重叠”的基础方法论。
* **阶段 3：Idea 收集、参考功能记录与切面边界确定 (Inbox Harvesting, Benchmark Logging & Bounds)**
  * **何时使用**：阶段 1 与 2 完成后，在需求收集或参考产品分析时触发。
  * **作用**：记录原始想法与参考产品功能点，归档图片素材并在文档中内嵌；创建功能点文档 (`D52-xx`)，建立与目标产品 AOP 切面的映射表，并通过「包含/不包含」界定切面边界。




* **阶段 4：需求列表与依赖拓扑设计 (Ticket Design & Dependency Graph)**
  * **何时使用**：切面边界确定后，进入具体研发需求拆解阶段。
  * **作用**：把切面功能点拆解为具体 Tickets (D40 Block)，建立三向 Markdown 映射并梳理前后置依赖 DAG 图谱。
* **阶段 5：优先级排列与交付 Roadmap (Prioritization & Roadmap)**
  * **何时使用**：需求 Tickets 拆解完成，准备规划版本迭代与交付节点时。
  * **作用**：Agent 呈现在阶段 4 梳理的需求拓扑，**引导并基于用户显式提供的优先级决策输入**，标注 P0/P1/P2 属性并划定里程碑 Roadmap（严禁 Agent 单方面代用户决策）。
* **阶段 6：多维复杂度建模与周期估算 (Complexity Modeling & Cost Estimation)**
  * **何时使用**：需要定量计算工时成本、评估跨团队沟通阻力与系统耦合膨胀时。为每个 Ticket 标注 6 维复杂度参数。
* **阶段 7：可交互网页预览与需求勾选计算器 (Web Dashboard & Interactive Preview)**
  * **何时使用**：准备向团队演示全景规划或进行交互式“需求勾选与成本测算”时。自动编译生成单文件离线可用的 `preview/index.html`。

---

## 📁 典型的项目产出目录结构 (Typical Output Directory Structure)

遵循本 Skill 策划产出的典型规范化项目目录树与层级约定，详见权威基准规范文档：
👉 **[00-typical-directory-structure.md](references/00-typical-directory-structure.md)**

---

## 📄 开箱即用的 Markdown 模板库 (templates/)

本 Skill 提供了覆盖产品策划全生命周期的 7 种标准文档模板，位于 `templates/` 目录：

* 📝 [D00-inbox-template.md](templates/D00-inbox-template.md) - **[阶段 3]** Idea 原始收集与切面映射模板
* 📝 [D10-narrative-template.md](templates/D10-narrative-template.md) - **[阶段 1]** 背景因果与平实定位叙事模板
* 📝 [D20-metrics-roadmap-template.md](templates/D20-metrics-roadmap-template.md) - **[阶段 1 & 阶段 5]** 度量指标与 Roadmap 里程碑模板
* 📝 [D30-aop-aspect-template.md](templates/D30-aop-aspect-template.md) - **[阶段 2 & 阶段 3]** AOP 切面（含【包含/不包含】边界与/roast-me）模板
* 📝 [D40-ticket-template.md](templates/D40-ticket-template.md) - **[阶段 4 & 阶段 5]** 需求 Ticket（含规约、前后置依赖与优先级）模板
* 📝 [D50-benchmark-analysis-template.md](templates/D50-benchmark-analysis-template.md) - 对标产品 AOP 拆解对标模板

---

## 核心方法论原则

1. **学术研究向语气 (Research-Oriented Tone)**：调动 `content-tone-adjuster`，开门见山陈述事实、机制与数据，禁止使用激情、战役化与非可验证词汇。
2. **面向切面关注点分离 (AOP Concern Separation)**：不以“功能点物理互斥”为硬性前提。一个具体的功能点可以同时归属于多个切面（切面代表不同的观察与业务关切视角）。
3. **全源输入向需求转化的 `/roast-me` 强质询原则 (Universal Input to Requirement via /roast-me)**：
   无论需求输入来自于对标竞品拆解 (`D52-xxxx`)，还是随意的对话交流与头脑风暴，在整理并导出项目 Ticket (`D40-xxxx`) 过程中，Agent **必须严格使用 `/roast-me` 展开多轮细粒度质询**。询问包含但不限于以下核心维度（保持合理的抽象度，并根据具体场景灵活扩展）：
   - **实现细节 (Implementation Details)**：交互控件、参数设定与边界条件；
   - **关联切面 (Related AOP Aspects)**：归属的 AOP 切面与架构映射（在 YAML 的 `related_aspects` 挂载）；
   - **未来特性关联 (Future Functionality)**：后续高级特性与演进接口的预留；
   - **已有需求互动 (Interaction with Past Tickets)**：与此前已建需求的状态保留与交互联动；
   - **风险与降级 (Risks & Fallbacks)**：安全隐患、性能上限与底层能力缺失时的降级策略；
   - 根据具体业务与工程场景灵活补充的其他维度。
4. **依赖拓扑与解耦交付 (Dependency Graph & Decoupling)**：建立需求与切面、叙事的双向映射，解耦前台体验与后台交付。

## 🛠️ 工作流阶段指南 (workflows/)

* [01-goal-and-narrative-alignment.md](workflows/01-goal-and-narrative-alignment.md) - **[阶段 1]** 目标与叙事对齐
* [02-aop-aspect-categorization.md](workflows/02-aop-aspect-categorization.md) - **[阶段 2]** AOP 切面划分
* [03-inbox-harvesting-and-aspect-bounds.md](workflows/03-inbox-harvesting-and-aspect-bounds.md) - **[阶段 3]** Idea 吸收与切面边界确定
* [04-ticket-design-and-dependency-graph.md](workflows/04-ticket-design-and-dependency-graph.md) - **[阶段 4]** 需求列表与依赖拓扑设计
* [05-prioritization-and-roadmap.md](workflows/05-prioritization-and-roadmap.md) - **[阶段 5]** 优先级与 Roadmap 确定
* [06-complexity-modeling-and-cost-estimation.md](workflows/06-complexity-modeling-and-cost-estimation.md) - **[阶段 6]** 复杂度建模与成本估算
* [07-web-dashboard-and-interactive-preview.md](workflows/07-web-dashboard-and-interactive-preview.md) - **[阶段 7]** Finder 列视图网页面板与 1-Hop 高亮编译规范

---

* 🛠️ **[scripts/extract_and_audit_mesh.py](scripts/extract_and_audit_mesh.py)** - AOP 需求架构 4 层提取与完整性审计 CLI 工具。扫描 D10~D40 节点提取 YAML/TOML/JSON 数据，审计裸切面、孤立 Ticket、破损死链、未评估项及未放进去的游离文件。
* 🛠️ **[scripts/compile_mesh_dashboard.py](scripts/compile_mesh_dashboard.py)** - AOP 需求架构全景 Dashboard 离线 HTML 网页全量编译脚本。编译导出 Zed Light 极简 Finder 4 列视图、三次贝塞尔圆滑连线、防抖动高亮描边、跨列置顶重排与遗漏审计弹窗的单文件离线 HTML 网页。

---

## 📚 参考规范与撰写指南 (references/)

* [00-typical-directory-structure.md](references/00-typical-directory-structure.md) - 规范化项目目录结构基准
* [08-how-to-describe-requirements-and-wireframes.md](references/08-how-to-describe-requirements-and-wireframes.md) - 需求表达与示意图绘制规范

