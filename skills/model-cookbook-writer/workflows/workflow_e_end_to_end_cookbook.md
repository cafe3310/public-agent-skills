# 工作流 E: 端到端 Cookbook 创建 (End-to-End Cookbook Creation)

本工作流规范了从收集背景信息到最终编译预览的完整 Cookbook 创建流程。它串联了工作流 A（参考摄取）、B（项目组织）、C（编译）的核心能力，并新增了 reference 文档管理和评测驱动开发的闭环机制。

---

## 1. 适用场景

当需要为一个特定模型从零创建完整的 Cookbook 交付物时使用。典型输入是：一组描述模型能力、评测数据和使用体验的背景文档 + 已有的 `cookbook-chapters/` 章节库。

---

## 2. 执行阶段

### Phase 1: 收集背景信息 (Collect References)

- **行动**:
  1. **确认背景文档**: 与负责人确认本次 Cookbook 所需的核心参考文档（如模型 Brief、评测数据分析、体验问题报告等）。可通过 `memocli find-doc-by-name` 从知识库搜索补充。
  2. **创建项目目录**: 在 `cookbooks/` 下创建项目目录，命名为 `YYYY-MM-DD_🟥_{model-name}_{cookbook-name}/`。注意：`_🟥_` 仅用于 cookbooks/ 项目目录名表示项目未完成，benches/ 和 bench-results/ 目录名不使用 emoji。
  3. **初始化 reference/**: 在项目目录下创建 `reference/` 子目录，将背景文档以英文 kebab-case 命名复制进来。保留原始文档的 frontmatter 和内容，不做改写。
  4. **撰写 readme.md**: 基于 reference 文档概述项目背景、目标模型、交付受众、reference 文档清单及各自用途。
  5. **初始化空文件**: 创建空的 `toc.md`（Phase 2 填充）和 `contents.md`（编译产物，禁止手写）。
  6. **归档旧项目**: 若存在同模型的旧 Cookbook 项目，重命名为 `_archived_` 前缀以退出编译范围。

- **交付物**: `cookbooks/<project>/` 目录含 `readme.md`、`reference/`（N 份文档）、空 `toc.md` 和空 `contents.md`。

### Phase 2: 筛选章节组建 TOC (Select Chapters & Build TOC)

- **行动**:
  1. **分析模型能力画像**: 从 reference 文档中提取模型的核心能力维度（如深度推理、代码执行、审美前端、SOP 提取等）和已知局限（如体验问题报告中的弱项）。
  2. **遍历章节库**: 扫描 `cookbook-chapters/` 全部章节，逐一判断与模型能力画像的匹配度。
  3. **推荐章节列表**: 按模型能力维度分组，列出推荐纳入的章节，标注匹配理由。同时列出建议排除的章节及原因。
  4. **请负责人审阅确认**: 将推荐列表提交负责人审阅。根据反馈调整后再进入下一步。
  5. **生成 toc.md**: 按确认后的章节列表生成 `toc.md`，遵循以下格式规范：
     - **扁平化**: 用 `H2/H3/H4` 前缀标记层级，不使用 Markdown 嵌套列表。
     - **状态在 WikiLink 内**: 状态标记（如 `🟥尚未完成`）放在 `[[path|显示文本 🟥尚未完成]]` 的显示文本部分。
     - **每项必须有描述**: 紧跟章节条目下方写一段文本，说明该章节在**这个 cookbook 项目**中存在的意义，关联到 reference 文档中的具体证据（Brief 章节、Benchmark 数据、体验问题编号等），而非泛泛描述章节本身。
     - **Bench/Result 子列表**: 挂载在章节条目之后、描述文本之前。
     - 格式示例参见工作流 B 步骤 3。

- **交付物**: 完整的 `toc.md`。

### Phase 3: 评测驱动开发 (Evaluation-Driven Development)

- **行动**:
  1. **遍历 TOC 中所有章节**: 逐一检查每个章节关联的 bench 和 bench-result 状态。
  2. **未开发的评测**: 若章节关联的 `benches/` 目录仅有占位 README，需开发完整的评测（README 四要素 + cases/ + test_runner.py）。
  3. **未执行的评测**: 若 bench 已开发但 `bench-results/` 为空或 state=pending，需执行评测并生成 `results.json` + `detail.json`。
  4. **已完成的评测**: 将评测结论反哺到章节 `content.md` 中，更新「本小节在说什么」段落。
  5. **更新状态标记**: 每完成一个章节的评测闭环，将 toc.md 中对应行的 `🟥` 更新为 `🟩`。
  6. **持续循环**: 重复上述步骤直到所有章节关联到评测结果。

- **交付物**: 所有章节的评测闭环完成，toc.md 无 `🟥` 标记。

### Phase 4: 衔接编译预览 (Assemble & Preview)

- **行动**:
  1. **编写衔接段落**: 为章节之间补充必要的过渡文本（前言、章节间衔接、总结等），写入对应的 content.md。
  2. **运行编译**: 执行 `python3 scripts/compile_cookbook.py <cookbook_path>`，生成 `contents.md`、`preview.html`、`preview.ipynb`。
  3. **审阅预览**: 打开 `preview.html` 通读全文，检查章节顺序、链接完整性和格式问题。
  4. **去除占位标记**: 确认所有内容完成后，将 cookbooks/ 项目目录名中的 `_🟥_` 移除。
  5. **TODO 收尾**: 在 `TODO.md` 中追加 `🟩` 完成条目。

- **交付物**: 完整的 Cookbook 交付件（contents.md + preview.html + preview.ipynb），目录名不含 `🟥`。

---

## 3. 约束规范

- **Reference 只读**: `reference/` 中的文档是背景输入，不应在开发过程中被修改。
- **TOC 唯一驱动**: 所有编译和进度追踪以 `toc.md` 为准。
- **筛选需确认**: Phase 2 的章节筛选结果必须经负责人审阅确认后才能写入 toc.md，不得自行决定。
- **评测闭环**: 没有关联到 bench-result 的章节视为未完成，整个项目保持 `🟥` 状态。
- **SourceRef 完整性**: 新建的任何 chapter 或 bench 文件必须含 frontmatter `sources:` 字段（详见 SKILL.md §4）。
