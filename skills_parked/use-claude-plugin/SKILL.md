---
name: plugin-search-and-use
description: 使用的 Claude Plugin 完成特定任务，可利用如 Knowledge Work Plugins 中的专业技能
author: github/cafe3310
depends_on_skill: []
depends_on_binary: []
---

# 检索和使用 Claude Plugin

此技能旨在帮助用户快速定位、理解并执行本地目录中的 Claude 插件（Plugins）及其关联的技能（Skills）。

## 工作流

### 1. 确认插件库目录
在开始检索前，必须确保用户已经将插件库所在的目录添加到当前上下文中。
- **内置库路径**：`skills/use-claude-plugin/knowledge-work-plugins`。
- 如果需要使用额外的库，请明确提示用户：“请先使用 `add dir` 命令添加包含 Claude 插件的根目录。”
- 确认目录下存在 `GEMINI.md` 或各子目录中包含 `.claude-plugin/plugin.json`。

### 2. 检索匹配的插件与技能
根据用户提出的具体任务（例如：“帮我做个竞品分析”或“审查这段代码”）：
- **扫描索引**：首先查阅插件库根目录下的 `GEMINI.md` 文件或参考下方的“受支持的插件库”列表，寻找与任务描述最匹配的插件名称。
- **深度定位**：
  - 进入对应的插件目录（如 `marketing/` 或 `engineering/`）。
  - 在 `skills/` 目录下寻找相关的子目录及其 `SKILL.md` 文件。
  - 阅读 `SKILL.md` 的 frontmatter 和描述，确认其功能是否覆盖用户需求。

### 3. 读取并遵循技能指令
一旦定位到正确的 `SKILL.md`：
- **解析工作流**：仔细阅读文档中的“Usage”、“How It Works”或“Workflow”章节。
- **识别工具要求**：检查是否需要特定的 MCP 连接器（参考插件根目录下的 `CONNECTORS.md` 或 `.mcp.json`）。
- **遵循格式规范**：严格按照 `SKILL.md` 中定义的输出格式（Markdown 结构、表格样式等）进行回复。

### 4. 执行任务
模拟该插件的身份，根据 `SKILL.md` 中的专家指令完成用户的具体任务。

## 注意事项
- **命名空间**：在引用或模拟执行时，应意识到插件的命名空间格式（例如 `/engineering:code-review`）。
- **降级处理**：如果相关的 MCP 连接器不可用，应按照插件文档中的“Standalone”模式运行，手动要求用户提供必要的输入。
- **反馈确认**：在执行前，可以简要告知用户：“我已找到 `[插件名]` 插件中的 `[技能名]` 技能，现在将按照该专家的标准为您处理任务。”

## 环境兼容性处理 (Gemini CLI)

由于本项目是基于 Claude 设计的，在 Gemini CLI 中调用这些插件时，Agent 需遵循以下适配规则：

| Claude 机制 | Gemini CLI 处理方式 |
| :--- | :--- |
| **Manifest (`plugin.json`)** | **仅参考**。获取插件元数据，不执行安装逻辑。 |
| **Skills (`skills/`)** | **重点阅读**。读取 `SKILL.md` 并将其指令注入到当前对话逻辑。 |
| **Commands (`commands/`)** | **视作普通指令**。按照 Markdown 中的步骤执行任务。 |
| **Hooks (`hooks.json`)** | **手动模拟**。Gemini 不会自动触发。若有必要，Agent 需手动执行钩子定义的命令（如 `npm run lint`）。 |
| **LSP (`.lsp.json`)** | **跳过**。Gemini CLI 暂不支持通过插件动态加载 LSP。 |
| **Settings (`settings.json`)** | **角色模拟**。根据 `agent` 字段调整语气和系统指令。 |

## 受支持的插件库 (来自内置插件库)

### Productivity (生产力)
- **task-management**: 基于 Markdown 的任务跟踪，管理 TASKS.md 文件。
- **memory-management**: 两层记忆系统（工作记忆与深度存储），学习用户术语和背景。
- **start**: 初始化任务、记忆系统并启动可视化仪表板。
- **update**: 分拣陈旧项目，检查记忆差距，并从外部工具同步数据。

### Engineering (工程)
- **code-review**: 审查代码的安全性、性能、正确性和可维护性。
- **incident-response**: 管理生产事故，包括分拣、通信、缓解和复盘。
- **system-design**: 设计系统和服务，包括架构图、API 设计 and 数据建模。
- **tech-debt**: 识别、分类并优先处理技术债。
- **testing-strategy**: 设计测试策略，涵盖单元、集成和端到端测试。
- **documentation**: 编写和维护技术文档、README 和运行手册。
- **standup**: 根据提交记录、PR 和任务自动生成站会更新。
- **architecture**: 创建或评估架构决策（ADR 格式）。
- **deploy-checklist**: 部署前验证，检查测试、依赖和回滚计划。
- **debug**: 结构化调试会话，涵盖复现、隔离、诊断和修复。

### Data (数据)
- **write-query**: 编写针对不同方言优化的 SQL。
- **validate-data**: 分析前的质量保证、方法论审查和偏差检查。
- **data-context-extractor**: 从数据源提取结构和元数据上下文。
- **sql-queries**: SQL 模式、最佳实践和性能优化。
- **build-dashboard**: 构建包含图表和过滤器的交互式 HTML 仪表板。
- **data-visualization**: 自动选择图表并生成可视化代码。
- **explore-data**: 探索数据集的形状、质量和模式。
- **statistical-analysis**: 描述性统计、趋势分析和假设检验。
- **analyze**: 回答数据问题，从快速查找至深度分析。

### Product Management (产品管理)
- **write-spec**: 从问题陈述生成功能规格书或 PRD。
- **roadmap-management**: 使用 RICE/MoSCoW 等框架管理路线图和优先级。
- **stakeholder-comms**: 生成针对不同受众（高管、工程等）的状态更新。
- **synthesize-research**: 将调研笔记和反馈转化为结构化洞察。
- **competitive-analysis**: 竞品功能对比、定位分析和战略建议。
- **metrics-tracking**: 设定目标 (OKRs)、设计指标层次和仪表板。
- **product-brainstorming**: 探索问题空间、生成点子并压力测试产品设想。

### Sales (销售)
- **account-research**: 研究公司或个人，获取新闻、联系人和雇佣信号。
- **call-prep**: 准备销售电话，包括背景研究和议程建议。
- **daily-briefing**: 优先级的每日简报，涵盖会议、管线提醒和建议行动。
- **draft-outreach**: 基于研究起草个性化的邮件和 LinkedIn 消息。
- **competitive-intelligence**: 竞品对比、定价情报和销售话术。
- **create-an-asset**: 生成定制销售资产，如着陆页、演示文稿。
- **call-summary**: 处理通话记录，提取行动项并起草后续跟进。
- **forecast**: 生成加权销售预测和缺口分析。
- **pipeline-review**: 分析管线健康度，识别风险并制定行动计划。

### Customer Support (客户服务)
- **ticket-triage**: 工单分类、优先级评估和路由建议。
- **customer-research**: 跨多渠道研究客户问题并综合答案。
- **response-drafting**: 根据场景和语调起草专业回复。
- **escalation**: 封装升级包，包含上下文、复现步骤和业务影响。
- **knowledge-management**: 从已解决的问题编写标准知识库文章。

### Marketing (市场)
- **content-creation**: 针对不同渠道的内容模板、标题公式和 CTA 指导。
- **campaign-planning**: 制定营销活动简报、渠道选择和成功指标。
- **brand-voice**: 执行品牌声音标准，管理术语和语气。
- **competitive-analysis**: 竞品调研、定位对比和战术手册创建。
- **performance-analytics**: 渠道指标分析、报告生成和优化框架。
- **seo-audit**: 关键词研究、页面分析和内容差距审计。
- **email-sequence**: 设计和起草多阶段邮件序列。

### Legal (法律)
- **contract-review**: 基于 Playbook 的合同分析、红线生成和影响评估。
- **nda-triage**: NDA 快速筛选和风险分类。
- **compliance**: 隐私法规 (GDPR/CCPA) 处理和 DPA 审查。
- **legal-risk-assessment**: 风险等级评估和升级标准。
- **meeting-briefing**: 会议上下文收集和行动项跟踪。
- **vendor-check**: 检查供应商现有协议状态。

### Finance (财务)
- **journal-entry-prep**: 凭证准备最佳实践、权责发生制和证明文档管理。
- **reconciliation**: 总账与子账、银行账单的对账及差异归因。
- **financial-statements**: 资产负债表、损益表生成及 GAAP 合规展示。
- **variance-analysis**: 差异分解（价格/数量等）和动因解释。
- **close-management**: 月末结账清单、任务排序和状态跟踪。
- **audit-support**: SOX 控制测试、样本选择和缺陷分类。

### Human Resources (人力资源)
- **recruiting-pipeline**: 管理招聘阶段，从筛选到录用。
- **comp-analysis**: 薪酬基准分析、职等分布和调整建议。
- **people-report**: 生成人员流失、多元化和组织健康报告。
- **performance-review**: 结构化绩效评估、经理模板和校准准备。
- **org-planning**: 编制规划、组织设计和团队结构优化。
- **interview-prep**: 创建结构化面试计划和评分表。
- **policy-lookup**: 查询员工手册，解释公司政策和福利。
- **onboarding**: 生成入职清单和第一周计划。

### Operations (运营)
- **process-optimization**: 识别流程瓶颈，减少浪费并优化工作流。
- **runbook**: 创建可重复的任务操作手册和检查清单。
- **compliance-tracking**: 跟踪审计、认证和政策遵守情况。
- **risk-assessment**: 识别运营风险并制定缓解措施。
- **vendor-review**: 供应商成本分析、风险评估和续约建议。
- **capacity-plan**: 资源容量规划和利用率预测。
- **change-request**: 创建变更申请，包含影响分析和回退计划。
- **status-report**: 生成面向领导层的状态报告和 KPI 更新。

### Enterprise Search (企业搜索)
- **search-strategy**: 将自然语言查询分解为跨源搜索指令。
- **knowledge-synthesis**: 跨多源数据综合答案并标注来源。
- **digest**: 生成每日或每周跨源活动摘要。
- **source-management**: 管理 MCP 数据源连接和优先级。

### Bio-Research (生物研究)
- **scientific-problem-selection**: 系统性研究问题选择框架。
- **single-cell-rna-qc**: 自动化的 scRNA-seq 数据质控。
- **scvi-tools**: 用于单细胞组学的深度学习分析工具。
- **nextflow-development**: 运行生物信息学分析流程 (nf-core)。
- **instrument-data-to-allotrope**: 将实验仪器输出转换为 ASM 标准格式。

### Cowork Plugin Management (插件管理)
- **cowork-plugin-customizer**: 定制现有插件的工具和工作流。
- **create-cowork-plugin**: 引导创建全新的插件结构。
