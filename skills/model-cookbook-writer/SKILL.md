---
name: model-cookbook-writer
description: 编写、丰富与编译 model cookbook 的专用人机协作开发工作流。包含 Prompting Guide 大纲扩展、行业参考 cookbook SourceRef 契约管理、交付物大纲拆解与初始化、TOC 驱动编译为 HTML/Jupyter Notebook 预览及知识库联动沉淀。
license: Apache-2.0
author: github/cafe3310
depends_on_skill: [cafe3310-obsidian-writer, memories-off]
depends_on_binary: [python3]
---

# Skill: model-cookbook-writer

本 Skill 定义了一套大模型应用 Cookbook 的全生命周期开发规范和人机协作工作流，覆盖策略调优、评测跑分、代码用例与最终交付物编译预览。

---

## 1. 仓库结构规范 (Repository Architecture)

大模型 Cookbook 仓库必须严格遵守以下目录结构和文件格式定义，以确保编译脚本能够自动解析和拼接。

```
<cookbook-repo>/
├── AGENTS.md                  # 项目章程与规范文件 (明确规则与协作流程)
├── TODO.md                    # 动态的任务积压与指派清单 (Log-driven Task Stream)
├── cookbook-chapters/         # 章节内容树 (存放理论、最佳实践及代码示例)
│   └── {chapter-name}/
│       ├── content.md         # 章节正文文本说明 (非叶子节点通常只包含此文件)
│       ├── benchmarks.md      # 评估该章节提示词机制的 micro-benchmarks 建议 (叶子节点专有)
│       └── examples.md        # 该章节的具体任务代码样例 (叶子节点专有)
│                              #   ↑ 三类文件均须含 YAML frontmatter 的 `sources:` 字段，
│                              #     声明对行业参考 cookbook 的引用关系，详见 §4「SourceRef 契约」。
├── benches/                   # 所有的微评测任务物理源码 (平铺命名)
│   └── YYYY-MM-DD_{bench-name}/
│       ├── README.md          # 评测目的、方式、对比分支及 Rubrics 四要素说明
│       │                      #   ↑ 同样须含 frontmatter `sources:` 字段。
│       ├── cases/             # 结构化的测试用例数据集 (如 test_cases.json)
│       └── test_runner.py     # 可独立运行的 Python 评测脚本
├── bench-results/             # 跑分数据客观归档 (平铺命名，与 benches 对应)
│   └── YYYY-MM-DD_{model-name}_{bench-name}/
│       ├── README.md          # 记录测试环境、简要结论与复现命令
│       ├── results.json       # 汇总跑出的评测指标结果 (包含 metrics、config 等字段)
│       └── detail.json        # 记录每个 case 的具体推理日志与判定详情
└── cookbooks/                 # 具体的 Cookbook 交付发布项目 (平铺命名)
    └── YYYY-MM-DD_{model-name}_{cookbook-name}/
        ├── readme.md          # 项目说明，介绍本次交付的背景、模型及受众
        ├── toc.md             # 编译主驱动大纲，扁平化列表 + H2/H3/H4 层级标记 + 描述文本
        ├── reference/         # 背景输入文档（只读，不参与编译）
        └── contents.md        # 编译产物：拼接合并后的正文大合集 (严禁手动在此处编辑内容)
```

### 核心目录详解
1.  **章节分类树 (`cookbook-chapters/`)**:
    *   **非叶子章节**: 仅用于大类框架，包含 `content.md`，用于对本大类机制做宏观概述。
    *   **叶子章节**: 真正的落地实现节点，必须同时包含 `content.md`、`benchmarks.md` 与 `examples.md`。
    *   *未开始编写的章节，其 Markdown 首行必须以 `🟥` 起头做待办标记。*
2.  **微评测任务 (`benches/`)**:
    *   平铺命名。未完工的评测任务在 `README.md` 中标注状态（如 `🟥 暂未执行该评测`），不在目录名中使用 emoji。
    *   `README.md` 中**必须**包含四要素：**评测目的、评测方式、对比方案、判定标准 (Rubrics)**。
3.  **跑分数据 (`bench-results/`)**:
    *   若评测尚未执行或正在执行，其 `README.md` 的状态需配置为 `Pending`，且 results.json 的 state 置为 `pending`。
    *   测试完成后，合入最终的 metrics 数据与 inputs/outputs 推理明细。
4.  **交付项目 (`cookbooks/`)**:
    *   大纲和正文彻底解耦。`toc.md` 扮演大纲路由，挂载物理文件的链接；`contents.md` 是编译生成的最终产物。

---

## 2. 核心工作流分支 (Decoupled Workflows)

本技能解耦为四个独立的工作流分支文件，指导开发助理（Agent）与负责人的不同阶段协作：

*   **[工作流 A: 摄取参考与扩展大纲 (Read & Extend Outline)](file://./workflows/workflow_a_ingest_references.md)**
    *   *场景*: 阅读官方最新提示词工程文献后，提炼核心策略与微评测任务并合入交付大纲。
*   **[工作流 B: 组织 Cookbook (Interactive Case Collection & Setup)](file://./workflows/workflow_b_organize_cookbook.md)**
    *   *场景*: 交互式盘点可用资产，定制 `toc.md` 物理引用关系并初始化新交付项目。
*   **[工作流 C: TOC 驱动编译与多格式预览 (TOC-Driven Compilation & Previews)](file://./workflows/workflow_c_toc_compile_preview.md)**
    *   *场景*: 运行脚本将大纲编译拼装为 `contents.md`、ScrollSpy 滚动高亮 `preview.html` 网页及状态机拆分的 `preview.ipynb` 笔记本。
*   **[工作流 D: 知识图谱与文档同步 (Knowledge Base & Vault Synchronization)](file://./workflows/workflow_d_sync_knowledge_base.md)**
    *   *场景*: 开发完结后，通过 `memocli` 非破坏性追加图谱并生成 Obsidian 📅 状态报告，执行 iCloud Git 同步优化。
*   **[工作流 E: 端到端 Cookbook 创建 (End-to-End Cookbook Creation)](file://./workflows/workflow_e_end_to_end_cookbook.md)**
    *   *场景*: 从收集背景 reference 文档开始，筛选章节组建 TOC，逐章节推进评测闭环，最终编译为完整交付物。串联 A/B/C 的核心能力，适用于为特定模型从零创建完整 Cookbook。

---

## 3. 微型范例仓库 (Example Assets)

为了直观地展示符合本 Skill 结构定义的仓库设计，在 [assets/example-cookbook-repo/](file://./assets/example-cookbook-repo/) 中建立了一个微型模拟仓库作为参考：

*   **项目章程与清单**:
    - [AGENTS.md (模拟项目章程契约)](file://./assets/example-cookbook-repo/AGENTS.md)
    - [TODO.md (模拟任务日志)](file://./assets/example-cookbook-repo/TODO.md)
*   **章节设计**:
    - [EXAMPLE-tool-calling/content.md (大类父章节)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/content.md)
    - [file-delimiters/content.md (叶子章节正文)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/content.md)
    - [file-delimiters/benchmarks.md (叶子章节评估说明)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/benchmarks.md)
    - [file-delimiters/examples.md (叶子章节代码用例)](file://./assets/example-cookbook-repo/cookbook-chapters/EXAMPLE-tool-calling/file-delimiters/examples.md)
*   **评测源码与结果**:
    - [benches/.../README.md (包含评测四要素说明)](file://./assets/example-cookbook-repo/benches/2026-01-01_EXAMPLE-different-delimeter-for-files/README.md)
    - [bench-results/.../results.json (客观指标跑分数据)](file://./assets/example-cookbook-repo/bench-results/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/results.json)
*   **发布交付物**:
    - [cookbooks/.../toc.md (TOC 树形驱动大纲)](file://./assets/example-cookbook-repo/cookbooks/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/toc.md)
    - [cookbooks/.../contents.md (拼接合成的最终正文)](file://./assets/example-cookbook-repo/cookbooks/2026-01-01_model-name_EXAMPLE-different-delimeter-for-files/contents.md)

### 3.1 章节文件模板 (Chapter File Templates)

`cookbook-chapters/` 下的三类文件须遵循固定的 heading 结构。模板文件位于 [assets/](file://./assets/)，创建新章节时以此为骨架：

*   **[TEMPLATE_content.md](file://./assets/TEMPLATE_content.md)** — 章节正文模板
    - `# 章节标题` → `## 本章节的内容` → `## 待确认的 Micro Benchmark 设计` → `## 引用来源文本` → `## 来源引用`
    - 含 YAML frontmatter `sources:` 声明引用关系
*   **[TEMPLATE_benchmarks.md](file://./assets/TEMPLATE_benchmarks.md)** — 评测指南模板（章节级索引，不写评测细节）
    - `# 评测指南` → `## 评测背景` → `## 关联的 Bench 项目`（列表形式引用 `benches/` 路径，含说明与结论反哺方式）
    - 无 frontmatter（引用关系由 content.md 承载）
*   **[TEMPLATE_examples.md](file://./assets/TEMPLATE_examples.md)** — 示例索引模板（章节级索引，不写示例全文）
    - `# 示例与 Recipe` → `## 示例背景` → `## 关联的示例`（列表形式，含适用模型、说明、对应 Bench 结论）
    - 无 frontmatter

---

## 4. 第三方 Cookbook 引用契约 (Third-Party SourceRef Contract)

本 Skill 管理的 cookbook 仓库大量借鉴自主流大模型厂商的官方 cookbook。**所有借鉴关系统一以 frontmatter `sources:` 字段声明，作为机器可读的单一事实源。**

### 4.1 物理镜像约定 (Local Mirror)

- 所有行业参考 cookbook 仓库应克隆到统一约定目录：`<workspace>/llm-cookbooks/<vendor>/`
- **引用必须使用「仓库根相对路径」**，而**不写绝对路径**，避免镜像目录迁移导致大规模引用失效。

### 4.2 SourceRef Schema

在 `cookbook-chapters/**/{content,benchmarks,examples}.md` 与 `benches/*/README.md` 的 YAML frontmatter 中以 `sources` 数组形式声明，单条目结构：

```yaml
sources:
  - vendor: <vendor-id>            # 厂商标识，如 openai, anthropic, google, qwen 等
    repo: <repo-name>              # 镜像根下的仓库名
    path: <relative/path/to/file>  # 相对仓库根
    registry_title: "..."          # 可选，上游 registry/title 原文
    registry_categories: [...]     # 可选
    binding_version: "..."         # 可选，强绑定某发版时填写
    upstream_url: https://...      # 上游文件的永久链接
    snapshot_commit: <commit-hash> # 锁版本，防上游漂移
    relation: borrows-from         # borrows-from | benchmarks-against | counter-example | extends
    outline_ref: "[5]"             # 可选，对应知识库大纲中的引用编号
    note: "..."                    # 可选，一句话说明为何引用 / 引用了哪一段
```

- **零 sources 不允许**：任何叶子章节或 bench 都该说明知识源头；如确属原创推导，写 `sources: []` 并在 note 注明「原创推导」。
- **snapshot_commit 锁定**：用于在上游 cookbook 仓库更新后能复现当时引用的版本。编译期可按此 hash 做引用有效性体检。

### 4.3 Relation 字段语义

| relation | 语义 |
|----------|------|
| `borrows-from` | 直接借鉴原文档思想 / 章节结构 / 代码骨架 |
| `benchmarks-against` | 把原文档当作评测 baseline 或对照组 |
| `counter-example` | 把原文档作为反例引用（如原方案在目标模型上劣化，本章节论证替代方案） |
| `extends` | 在原文档基础上做了显著扩展（新增覆盖维度、组合多家方法） |

### 4.4 批量回填脚本范式

当行业参考 cookbook 大规模新增 / 章节大量铺设时，**禁止逐文件手改 frontmatter**，必须以一次性脚本批量注入。`scripts/` 下提供两种范式脚本：

- **插入模式脚本**：对**无 frontmatter** 的文件前置注入；幂等：已有 `sources:` 字段则跳过。适用于首次引入某 vendor 的引用。
- **追加模式脚本**：对**已有 frontmatter** 的文件，向 `sources:` 数组**追加**新条目，按 (vendor, path) 去重，保留原有引用。适用于在已有引用上叠加新 vendor 引用。

两类脚本共享核心结构：`SOURCES` 字典声明引用元数据 + `TARGETS` 字典声明文件→引用映射 + `render_*` 函数渲染 YAML。**新增 vendor 时**复用同一范式。

### 4.5 派生章节脚手架范式

当从行业参考 cookbook 整合出大纲尚未覆盖的方向，**必须同时创建 chapter 与配套占位 bench**，且全部带正确的 SourceRef frontmatter。范式脚本以 `dataclass Spec` 声明（章节路径、标题、简介、bench slug、bench 目的、rubrics、SourceRef 列表）批量生成 3+3 文件结构（chapter 三件套 + bench README/runner/cases）。

### 4.6 编译期处理 (compile_cookbook.py 待扩展)

`scripts/compile_cookbook.py` 在编译 `contents.md` / `preview.html` / `preview.ipynb` 时，应增加 `merge_sources` pass（**当前未实现**，挂账于宿主仓库 TODO）：

1. 扫描所有被 `toc.md` 引用的 chapter / bench frontmatter 的 `sources` 数组。
2. 在每个章节末尾自动注入引用块（Markdown 形式），格式如 `> **Sources**: [<filename>](upstream_url) — <vendor>, relation: borrows-from`。
3. 在交付件根输出一份 `sources_index.md`，按 `vendor / repo` 二级分组反向索引「我们引用了谁的哪些文档」，便于版权与合规审计。
4. 在 `preview.ipynb` 中向对应 markdown cell 注入同样引用块，并在第一节正文之前加一节「**Acknowledgements & Sources**」放总索引。

### 4.7 与 Obsidian 大纲的协同

- Obsidian 端的核心交付物大纲中「已阅读 / 待阅读参考文档」清单，是 SourceRef 数据库的**人读视图**。
- 任何 chapter / bench 的 sources 新增、变更，须同步反映到 Obsidian 大纲；反向，Obsidian 大纲新增「待阅读」时，落地到代码仓库 chapter 后应立刻把对应条目从「待阅读」迁移到「已阅读」。

---

## 5. 自动化编译工具说明 (Compiler CLI)

本 Skill 在 `scripts/` 目录下搭载两个编译预览工具：

### 5.1 全局章节浏览器 — `compile_preview.py`（日常审阅首选）

当用户说「html 预览」「编译预览」「看一下章节」时，优先使用此脚本。

*   **执行方式**:
    ```bash
    python3 scripts/compile_preview.py
    ```
*   **产出**: `build/preview.html` — 单文件自包含 HTML（约 600-800KB），双击即可离线浏览，无需起 server。
*   **页面结构**:
    - 左侧 Tab 切换栏 + 树形/列表目录
    - 右侧 Markdown 正文渲染（marked.js + highlight.js 代码高亮）
*   **左侧 Tab 目录源**（按优先级）:
    1. **Prompting Guide** — 扫描 `cookbook-chapters/02-prompting-guide/` 递归树
    2. **主题 Cookbook** — 合并 `04-methodology-cookbooks/` + `06-multimodal/`
    3. **特定任务** — 扫描 `cookbook-chapters/05-task-recipes/`
    4. **各 cookbook 交付件** — 扫描 `cookbooks/*/toc.md` 自动生成 Tab
*   **内容内嵌机制**: 编译时读取所有 `content.md` / `benchmarks.md` / `examples.md`，剥离 frontmatter 后以 base64 JSON 嵌入 HTML。点击左侧目录项，JS 从内存取对应章节渲染到右侧。
*   **右侧功能**:
    - 面包屑路径导航
    - 子 Tab 切换（正文 / Benchmarks / Examples）
    - 占位章节友好空状态提示
*   **设计约束**:
    - 全静态单文件，零外部文件依赖（CDN 加载 marked.js / highlight.js）
    - 自动从 `content.md` 首行 `#` 标题提取显示名，剥离 `✏️🟥` 前缀
    - 占位判定：目录名含 `🟥` 或 content.md 前 200 字符含 `🟥`

### 5.2 单 Cookbook 交付编译 — `compile_cookbook.py`

*   **执行方式**:
    ```bash
    python3 scripts/compile_cookbook.py <cookbook_directory_path>
    ```
*   **产出位置**: `build/<cookbook_folder_name>/`（含 `contents.md`、`preview.html`、`preview.ipynb`）
*   **适用场景**: 将特定 cookbook 交付项目的 `toc.md` 编译为正式交付物格式（含 ScrollSpy 暗色主题 HTML、Jupyter Notebook）。
*   **待扩展**: `merge_sources` pass —— 参见 §4.6。

---

*产出目录 `build/` 已由项目根目录的 `.gitignore` 排除，保持 Git 环境整洁。*

---

## 6. Prompting Guide 章节整理方法论 (Chapter Refinement Methodology)

本节规范了 `cookbook-chapters/02-prompting-guide/` 下每个 `content.md` 的整理范式。该方法论仅适用于 prompting guide 类章节，不适用于其他类型章节。

### 6.1 content.md 三段式结构

整理后的每个 content.md，在 frontmatter 和标题之后，必须包含以下三个小节（用 `---` 分隔线与标题隔开）：

```markdown
# ✏️🟥 章节标题

---

### 本小节在说什么

（从读者角度描述本章节要传达的信息点。不复述参考来源，而是提炼出目标模型 cookbook 要教给读者的内容。）

### 为了完成本小节需要的结果，需要做什么 micro benchmark

（列出可评测的对比实验，每条都是「改变 X 变量，观察 Y 指标」的形式。）

### 在引用来源中，本小节的文本部分都包含什么

（从 SourceRef 引用的源 notebook 中提取相关文本，按 outline_ref 分组引用。）
```

### 6.2 「本小节在说什么」的撰写规范

此段由人工撰写（或人机协作后由人工确认），遵循以下原则：

1. **站在目标模型读者角度**，而非复述参考来源。从参考来源的核心主张中提取「差异维度」，归纳为统一主题下的几个子方面。
2. **过滤厂商特有内容**：只保留通用 prompting 方法论，排除厂商特有的产品工具或 API 细节。
3. **承诺评测验证**：结尾应指向「经过我们评测更加有效的做法」，而不是止步于介绍。

### 6.3 「micro benchmark」的撰写规范

此段将参考来源中的每个「建议/主张」转化为可评测的对比实验：

1. **每条 benchmark 都是对比设计**：明确写出变量（要改变什么）和指标（观察什么效果）。对比的选项直接从参考来源的不同做法中提取。
2. **补充参考来源未覆盖的维度**：如果有逻辑上需要验证但三家都未提及的假设，也应加入。
3. **产出推荐示例**：最后一条通常是「给出目标模型建议的格式例子」，意味着 benchmark 的产出不仅是数据，还要形成可纳入正文的推荐模板。

### 6.4 「引用来源文本」的提取规范

此段由 Agent 从源 notebook 中提取，遵循以下原则：

1. **只提取 text/markdown cell**，跳过 code cell。
2. **按 outline_ref 分组**，每组用 `#### [ref] 来源标题 — 章节名` 作标题。
3. **原文引用**（英文原文不翻译），用 blockquote `>` 格式。
4. **只保留与本章节主题相关的段落**，跳过无关内容。如果源 notebook 有大量与本章节无关的内容，在末尾用括号注明被省略的部分及原因。

### 6.5 整理工作流

1. Agent 读取目标 content.md 的 SourceRef frontmatter，确认引用来源列表。
2. Agent 从 `<workspace>/llm-cookbooks/` 下的源 notebook 中提取与本章节主题相关的 text cell，填入「引用来源文本」段。
3. 「本小节在说什么」和「micro benchmark」两段留空（标注「待填写」），等待用户填写或确认。
4. 用户填写 / 修改前两段后，Agent 可根据用户确认的范式批量铺开其余章节。

---

## 7. 技能包待办事项 (TODO & Roadmap)

本 Skill 目前专注于 Cookbook 的大纲提炼、用例组织、SourceRef 契约维护、TOC 驱动编译和两库联动记录，**尚未包含**以下核心开发环节的工作流与规范：
*   🟥 **开发评测 Framework**：即 `bench-framework/` 基座项目（模型 API client、判定逻辑 judge、执行度量 runner）的开发与维护规范。
*   🟥 **开发评测任务**：即 `benches/` 目录下具体测试用例集设计、`test_runner.py` 逻辑实现及本地联调的开发工作流。
*   🟥 **`compile_cookbook.py` 的 `merge_sources` pass 实现**：参见 §4.6。
