# Workflow: Knowledge Extraction (Sub-agent Driven & Multi-stage)

本工作流通过 **多阶段原子提取 (Multi-stage Atomic Extraction)** 降低复杂任务的熵值，并利用 **`knowledge-extractor` 子代理** 实现超长上下文的自动化分段处理与断点续传。

## 核心工具
- **SCRIPT_extract_knowledge.py**: 基于 `02` 提取 `01` 内容，支持 `full` 和 `incremental` 模式。
- **knowledge-extractor (Sub-agent)**: 专门负责从超长聊天记录中进行分块 (Chunk) 提取与增量合并。

## Phase 1: 任务初始化 (Job Initialization)

1.  **[Main Agent]**: 确认项目定义 `kb/02-project-specs/*.yaml` 中的 `strategy` 参数（`full` 或 `incremental`）。
2.  **[Main Agent]**: 运行 `SCRIPT_extract_knowledge.py --spec-file <spec_path>`。
3.  **[Script]**: 执行自动化准备：
    - **Full Contexts**: 导出项目定义的聊天语料至 `contexts.md`。
    - **Delta Contexts (Incremental Only)**: 
        - 若 `strategy` 为 `incremental`，脚本会自动对比上一次运行的 `contexts.md`。
        - 使用 `diff` 算法提取新增行，保存为 `added-contexts.md`。
        - 若无增量，脚本将报告状态并终止，防止冗余运行。
    - **Instructions**: 为 YAML 中的每一个 `extraction_goals` 生成对应的 `prompts-{idx}-{title}.md`。
    - **State**: 在 `kb/tasks/` 下为每个目标初始化进度管理文件 `task_{idx}.yaml`。
4.  **[Main Agent]**: 根据 `strategy` 结果，路由至对应的上下文路径（`contexts.md` 或 `added-contexts.md`）。

---

## Phase 2: Sub-agent 调度与任务隔离 (Strict Task Isolation)

此阶段由主 Agent 按照 YAML 定义的任务顺序，**串行**调度位于 `agents/im-local-db_knowledge-extractor.md` 的子代理。

### 1. 任务隔离规约 (Task Isolation Rules)
- **串行原则**: 必须先完整处理并合并 Goal 1，才能启动 Goal 2。严禁在一次 Chunk 循环中合并处理多个 Prompt。
- **启动参数**:
  - **`CONTEXT_PATH`**: 根据策略指向 `contexts.md` 或 `added-contexts.md`。
  - **`PROMPT_PATH`**: **仅指向当前目标的一个 Prompt**。
  - **`STATE_PATH`**: 对应的任务状态文件。
  - **`OUTPUT_DIR`**: 存放分块结果的目录。

### 2. 交互指令模板
主 Agent 应使用以下格式启动子代理：
> “请启动 `knowledge-extractor` 子代理。
> 任务目标请参考 `{{PROMPT_PATH}}`。
> 输入语料为 `{{CONTEXT_PATH}}`。
> **隔离输出规约**：请将每个 Chunk 的提取结果独立保存为 `output-{{STAGE_IDX}}-chunk-{{CHUNK_NO}}.md`。
> 状态同步至 `{{STATE_PATH}}`。
> [如有依赖] 请结合 `{{DEP_PATH}}` 中的已有发现进行深度关联分析。”

---

## Phase 3: 子代理自动化执行逻辑 (Internal Logic)

子代理进入独立上下文，执行 **Map 阶段**（提取）：

### 1. 状态感知与断点续传 (Resuming)
- 子代理读取 `STATE_PATH`，识别 `chunk_list` 中的 `status`（已处理的块）。
- 若任务曾中断，自动定位到下一个 `pending` 状态的块。

### 2. 分段隔离提取 (Map Phase)
- **读取**: 按照 `chunk_list` 定义的范围（如 1-1000 行）读取片段。
- **提取**: 基于 `PROMPT_PATH` 的要求，分析该片段中的知识点。
- **持久化**: 将该片段产出写入独立的 `output-{{STAGE_IDX}}-chunk-{{CHUNK_NO}}.md`。**严禁直接修改或覆盖其他分块文件**。

### 3. 状态回写 (Check-pointing)
- 每处理并成功写入一个 Chunk 文件后，子代理必须立即更新 `STATE_PATH` 中对应块的状态为 `done`。

---

## Phase 4: 零损耗物理整合 (Zero-Loss Physical Merge)

当当前 Goal 的所有分块任务完成后，由 **主 Agent** 执行物理合并，严禁调用 LLM 生成摘要。

1.  **收集**: 在 `RUN_DIR` 目录下读取所有 `output-{{STAGE_IDX}}-chunk-*.md` 文件。
2.  **物理拼接 (Reduce Phase)**: 
    - 使用 Shell 命令（如 `cat output-XX-chunk-*.md > output-XX.md`）按编号顺序将所有分块内容拼接到最终文档。
    - **严禁对内容进行摘要、改写或删减。** 必须确保 100% 的提取内容被保留。
3.  **索引生成 (Optional)**: 合并完成后，可以调用 LLM 为生成的长文档添加一个目录（TOC），但不得修改正文。
4.  **状态流转**: 合并完成后，将 `task_XX.yaml` 标记为 `COMPLETED`，随后根据需要启动下一个 Goal。

---

## 任务完成标志

- **[Output]**: 当所有 `extraction_goals` 对应的 `output-{idx}.md` 文件均在执行目录下生成且任务状态为 `COMPLETED` 时，流程结束。
- **[Audit]**: 每一个提取出的知识点必须保留 `[来源: 文件名/日期]` 的标记，确保 100% 可追溯。

---

## 异常处理规约
- **数据冲突**: 若合并新分段时发现与旧结果冲突，子代理需保留原始证据并追加新的信息，在结果中并列呈现。
