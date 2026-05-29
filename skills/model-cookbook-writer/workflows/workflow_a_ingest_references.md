# 工作流 A: 摄取参考与扩展大纲 (Read & Extend Outline)

本工作流规范了如何摄取业界前沿大模型的 Prompting Guides 原始文献，并将其提炼的核心策略与微评测任务合并补充至项目交付大纲中。

---

## 1. 执行步骤

### 步骤 1: 阅读参考与事实提取
- **输入**: 指定的参考提示词指南文件（如 `*.ipynb` 或 `*.md`，通常位于工作区的参考文件夹下）。
- **行动**:
  1. 通过解析工具阅读文献，系统提炼文献中关于此模型的最优 prompting 策略。
  2. 提取出以下三类关键事实：
     - **提示词层面的 XML 结构化标签** (如 `<context_gathering>`, `<persistence>`, `<solution_persistence>`)。
     - **API 级别或字段级的底层机制** (如 `reasoning_effort`, `previous_response_id`, `strict`, `/responses/compact`)。
     - **业界的典型 Prompt Tuning 调优经验** (如协作编码 verbosity 双重控制、proactive edits 主动修改实践)。
  3. 提炼或构造相应的微型评测任务（Micro-benchmarks）或开发用例。

### 步骤 2: 识别冲突与章节规划
- **输入**: 当前工作区的 Cookbook 交付物大纲源档（如 `YYYY-MM-DD-HH-mm-大纲源档-*.md`）。
- **行动**:
  1. 交叉对比大纲已有内容，识别出新机制在大纲中的遗漏点。
  2. 规划应该新增/顺延的章节，确定其在 `02. Prompting Guide 结构大纲` 下的具体小节编号（如 `### 第三节 ...`）及子标题。
  3. 决定是否需要将某些底层字段与 API 参数合并收集，放置在 `## 03. 特殊机制与结构化 Tag 收集说明` 章节中。

### 步骤 3: 提案寻求负责人确认
- **行动**:
  1. 明确、自然地向项目负责人汇报从文献中提炼的核心特性。
  2. 提供大纲演进方案，明确列出拟新增的章节结构、标题层级，以及配套的 `✏️ 评测/开发任务` 规划。
  3. 询问项目负责人是否同意此大纲演进方案。**在未获得明确确认前，不得擅自修改大纲文件。**

### 步骤 4: 精准实施大纲增改
- **触发**: 项目负责人对演进提案给予肯定确认。
- **行动**:
  1. 遵守**手术式精准修改原则**，使用代码编辑工具对大纲源档文件执行局部、精准的增删改。
  2. 将新提取的特质和评测任务按规范编入对应小节中：
     - 所有的提示词技巧说明，均以数字列表或无序列表的形式陈述，并在句尾加上引用文献序号（如 `[3]`）。
     - 所有的 micro-benchmark 评测任务必须以 `✏️ 评测任务：...` 的特定 Emoji 格式规范标注。
  3. 自动顺延和调整大纲后续章节的中文数字序号（如 `第三节` 改为 `第四节`），确保全文目录层级一致，无编号断裂。
  4. 如果将某部分升级为大章节，注意更新其下属子标题的 Markdown 层级（如由 `####` 升为 `###`）。

### 步骤 5: 登记 SourceRef（机器可读引用契约）
- **触发**: 当本次摄取的是行业参考 cookbook 中的具体 notebook / md 文档时（不仅仅是阅读笔记）。
- **行动**:
  1. **物理镜像核对**：确认源仓库已镜像到 `<workspace>/llm-cookbooks/<vendor>/<repo>/` 约定目录；记录其当前 HEAD commit hash（即 `snapshot_commit`）。
  2. **识别落点**：判断本次引用应挂载到哪些 chapter（`cookbook-chapters/**/{content,benchmarks,examples}.md`）或 bench（`benches/*/README.md`）的 frontmatter `sources:` 数组中。
  3. **批量回填**：参考 `scripts/` 下的插入模式或追加模式范式脚本，一次性注入。**禁止逐文件手改 frontmatter**。
  4. **Schema 合规**：每条 source 必须含 vendor / repo / path / upstream_url / snapshot_commit / relation 六个必填字段；relation 取值 ∈ {borrows-from, benchmarks-against, counter-example, extends}。详见 SKILL.md §4。
  5. **Obsidian 大纲同步**：把对应条目从大纲「待阅读参考文档」迁移到「已经完成阅读的参考文档」，确保两库一致。

### 步骤 6: Commit 与同步优化
- **行动**:
  1. 对修改后的大纲文件、frontmatter 批量回填脚本、被注入的 chapter/bench 文件执行 `git add` 和 `git commit`（commit message 中明确标注本次 SourceRef 变更涉及的 vendor 与条目数）。
  2. **iCloud 备份优化**: 在前台执行 `git gc`，强制打包 loose objects，以防同步冲突并优化 iCloud 传输速度。

---

## 2. 约束规范

- **主动性**: Agent 应主动列出待读文献、主动识别冲突和重构机会，但禁止未经确认擅自更改。
- **引用规范**: 任何新合入的内容必须在句尾显式按 `[1]`, `[2]`, `[3]` 格式标注引用来源；**行业参考 cookbook 的引用必须同时落到 SourceRef frontmatter（参见步骤 5）**。
- **SourceRef 完整性**: 严禁出现引用了行业参考 cookbook 内容但 frontmatter 缺 `sources:` 字段的情况；如属于原创推导，应显式写 `sources: []` 并在 note 中注明。
