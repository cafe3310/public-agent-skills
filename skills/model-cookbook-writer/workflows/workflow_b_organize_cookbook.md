# 工作流 B: 组织 Cookbook (Interactive Case Collection & Setup)

本工作流规范了如何通过与项目负责人交互式沟通，收集特定主题下的用例（cases/benches）和章节，并物理初始化对应的 Cookbook 交付项目。

---

## 1. 执行步骤

### 步骤 1: 交互式收集需求与用例
- **行动**:
  1. **明确主题与模型**: 主动询问负责人拟产出的 Cookbook 针对什么模型以及什么主题（如 `tool-calling`、`structured-outputs`、`agent-orchestration` 等）。
  2. **盘点可用资产**: 扫描当前仓库的 `cookbook-chapters/`、`benches/` 和 `bench-results/`，列出与该主题相关的所有已有章节、评测任务和已跑出数据的评测结果。
  3. **确认包含用例**: 通过交互式提问（或提出推荐的用例列表），让负责人确认本次 Cookbook 编译中拟包含的 Chapters、Benches 和 Results。

### 步骤 2: 物理创建交付项目目录
- **行动**:
  1. **确定命名与路径**: 在 `cookbooks/` 目录下创建平铺的项目文件夹。命名规范为：`YYYY-MM-DD_{model-name}_{cookbook-name}`。
     *   *若该 Cookbook 包含未完工的内容/评测，则命名中加入 `_🟥_`（仅限 cookbooks/ 项目目录名），例如：`YYYY-MM-DD_🟥_{model-name}_{cookbook-name}`。benches/ 和 bench-results/ 目录名不使用 emoji，未完成状态在其 README.md 中标注。*
  2. **初始化核心文件**:
     - 创建 `readme.md`：记录此 Cookbook 的主题、适用模型、受众、以及所基于的最佳实践来源。
     - 创建 `toc.md`：核心驱动大纲（参见步骤 3 的 TOC 规范）。
     - 创建 `contents.md`：空文件，或仅包含基本大标题。该文件后续由编译脚本自动填充，严禁手动在此处写入正文。
  3. **章节 / Bench 物理初始化的 SourceRef 要求**: 当本工作流的盘点过程中发现 `cookbook-chapters/**/{content,benchmarks,examples}.md` 或 `benches/*/README.md` 尚未存在而需要新建时，**新建文件必须包含 YAML frontmatter `sources:` 字段**（详见 SKILL.md §4 第三方 Cookbook 引用契约）：
     - 若该章节/bench 借鉴自行业参考 cookbook，须按 SourceRef Schema 列出至少一条 source 条目；
     - 若属于原创推导，须显式写 `sources: []` 并在注释中说明「原创推导」；
     - **派生章节批量铺设**：若一次需要创建多个 chapter + 配套 bench，参考 `scripts/` 下的脚手架范式脚本（dataclass `Spec` 模式），避免逐文件手写 frontmatter。

### 步骤 3: 编写 TOC 驱动大纲 (toc.md)
- **行动**:
  1. 在 `toc.md` 中以扁平化列表定义 Cookbook 大纲。用 `H2/H3/H4` 前缀标记章节层级，避免 Markdown 嵌套列表。
  2. 每个章节条目使用 WikiLink 关联到 `cookbook-chapters/` 下的 `content.md`。
  3. 状态标记（如 `🟥尚未完成`）放在 WikiLink 的显示文本部分（`|` 后面），不放在列表项前面。
  4. 每个章节条目下方紧跟一段描述文本，说明**该章节在这个 cookbook 项目中存在的意义**（而非章节本身的通用描述）。描述应关联到 reference 文档中的具体证据。
  5. 需要挂载评测的章节，Bench 和 Result 以子列表形式跟在章节条目之后、描述文本之前。
  6. **TOC 结构规范示例**:
     ```markdown
     ## 章节分组标题

     - H2: [[cookbook-chapters/02-prompting-guide/02-agentic-workflow/content.md|在进行 Agentic Workflow 时的建议]]
       本 cookbook 中，这一章是核心——目标模型的 agent 工作流是其首要应用场景。

     - H3: [[cookbook-chapters/02-prompting-guide/02-agentic-workflow/system-prompt/content.md|关于「System Prompt」]]
       - Bench: [[benches/2026-05-29_system-prompt-styles/README.md|system-prompt-styles 🟥尚未完成]]
       - Result: [[bench-results/2026-05-29_<model-name>_system-prompt-styles/README.md|Result 🟥尚未完成]]
       目标模型在不同 harness 下表现参差，system prompt 结构直接影响稳定性。
     ```

### 步骤 4: 任务流追加与状态标记
- **行动**:
  1. 交叉检查 TOC 挂载的内容。如果引用的 Chapters、Benches 或 Results 中包含 `🟥` 占位，则在此 Cookbook 的 `toc.md` 对应节点旁，以及整个项目的根目录 `TODO.md` 中，追加相应的 `🟥` 任务条目。
  2. 使用统一的任务追踪格式追加在 `TODO.md` 的 Task Stream 中，例如：
     ```markdown
     - YYYY-MM-DD HH:mm 🟥 补充 {cookbook-name} 引用的 {bench-name} 评测用例与 runner 代码
     ```
  3. 向负责人汇报项目已成功初始化，列出生成的 `readme.md` 和 `toc.md` 的路径，并展示当前待办任务，等待下一步开发指派。

---

## 2. 约束规范

- **TOC 唯一驱动**: 任何 Cookbook 的生成必须通过 `toc.md` 引导。不得在 `contents.md` 中直接进行手动拼装或硬编码。
- **状态一致性**: 若 Cookbook 包含未完成的评测（`benches/` 带有 `🟥`），整个 Cookbook 目录名和 `toc.md` 中必须包含 `🟥` 标志，直至评测数据完全跑出并合入 `bench-results/`。
- **SourceRef 完整性**: 新建的任意 chapter `content.md / benchmarks.md / examples.md` 与 bench `README.md`，frontmatter 必须含 `sources:` 字段。详见 SKILL.md §4。
