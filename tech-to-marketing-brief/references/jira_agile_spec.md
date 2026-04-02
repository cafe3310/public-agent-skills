# 研发任务转化规范 (Jira Ticket & Agile Spec)

> 本文档融合了 Claude Plugin 中 `Product Management: write-spec` 与 `Engineering: documentation` 的标准工作流。用于指导如何将营销需求逆向拆解为研发任务。

## 1. 为什么营销需要 Jira Ticket？
一次成功的发版宣发，除了市场侧的吹嘘，还需要产品/研发侧提供强有力的“弹药库”（如定制的 Agent 模板、前端发光按钮、预设的 Prompt 拦截器）。
此模块负责将“宣发噱头”落地为“开发可执行的需求”。

## 2. 任务输出格式规范 (Ticket Anatomy)
每生成一个 Jira 任务，必须遵循标准的敏捷开发规范：

### [Issue Type] 标题
- 类型通常为 `[Story]` 或 `[Task]`。
- 标题格式：`[宣发支撑] 描述需增加的核心功能`（如：`[宣发支撑] 在 Ling Studio 预置"文案除味大师" Agent Skill`）。

### 1. User Story (用户故事)
- **As a** (作为一个...): [目标用户群体，如“受小红书评测吸引而来的文科生小白”]
- **I want to** (我想要...): [执行的具体动作，如“一键使用这套复杂的四步除味提示词”]
- **So that** (以便于...): [达成的业务价值/商业目的，如“降低使用门槛，提升产品留存与 Token 消耗”]

### 2. Acceptance Criteria (验收标准 / AC)
- 必须清晰、可测试、无歧义。采用 `Given / When / Then` 句式更佳。
- 示例：
  - AC1: 在“模型技能”下拉菜单中，新增名为「自媒体文案除味大师」的预设模板。
  - AC2: 用户点击后，输入框默认填充包含“四步引导法”的 System Prompt。
  - AC3: 需支持变量槽位 `{{参考样板文章}}` 与 `{{新的核心主题}}`。

### 3. Engineering Notes (研发提示 / 可选)
- 给出 API 对接层、网关层（Harness）或前端埋点（如 UTM 参数追踪）的具体实现建议。