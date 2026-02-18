# 任务启动：知识提取子代理 (Sub-agent Launch)

你将作为主 Agent，协调 `knowledge-extractor` 子代理完成以下提取任务。

## 任务详情
- **项目 ID**: {{PROJECT_ID}}
- **当前阶段**: {{STAGE_IDX}} - {{STAGE_TITLE}}
- **核心文件**:
  - Context File: `{{CONTEXT_PATH}}`
  - Instruction File: `{{PROMPT_PATH}}`
  - Output Directory: `{{RUN_DIR}}` (分块产出存放地)
  - State File: `{{STATE_PATH}}`
  - (可选) Dependency File: `{{DEP_PATH}}`

## 启动指令
请通过调用工具 `knowledge-extractor` 来启动提取过程。

### 传参要求 (Parameters)
1.  **prompt**: 请参考 `{{PROMPT_PATH}}` 中的提取目标。
2.  **context_path**: 指向 `{{CONTEXT_PATH}}`。
3.  **state_path**: 指向 `{{STATE_PATH}}`。
4.  **output_dir**: 指向 `{{RUN_DIR}}`。
5.  **dependency_path**: (若有) 指向 `{{DEP_PATH}}`。

### 运行规约 (Execution Rules)
- 要求子代理以 **1000 行/Chunk** 的步长进行分段读取。
- **隔离命名规约**：强制要求子代理将每个 Chunk 的产出保存为 `output-{{STAGE_IDX}}-chunk-{{CHUNK_NO}}.md`。
- 要求子代理在每次写入分块文件后，必须更新 `{{STATE_PATH}}` 中对应 Chunk 的状态为 `done`。
- 任务完成后，请子代理向你汇报所有分块文件的保存目录。
