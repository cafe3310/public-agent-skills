# Workflow: Ingest & Normalize

## 核心工具
- **SCRIPT_normalize_merge.py**: 基于 `02` 的定义，清洗 `00` 目录，归档到 `01`。
    - **Args**: `--input_dir kb/00-chats-input-raw --output_dir kb/01-chats-input-organized --knowledge_base_dir kb [--fallback_year YYYY]`
    - **Note**: `--fallback_year` 用于在原始日志中时间标签缺少年份（如 `02-06`）时提供默认年份。
- **SCRIPT_log_merger.py**: 对单个或多个文件执行记录合并，处理重叠。

## Phase 1: 防御性备份 (Safety First)
1.  **[System]**: 检测 `00-chats-input-raw` 目录下是否存在 `.md` 文件。
2.  **[Script]**: 调用 `workflows/util_backup/SCRIPT_backup_full.py`。
    - *Action*: 全量备份 `kb` 目录。
3.  **[Agent]**: 确认备份成功。如果失败，终止流程并报错。

## Phase 2: 数据清洗与归档 (ETL)
1.  **[Script]**: 调用 `SCRIPT_normalize_merge.py`。
    - *Input*: `kb/00-chats-input-raw`
    - *Output*: `kb/01-chats-input-organized`
    - *Task Audit*: `kb/tasks/merge/run_{run_id}/` (存储原始分块与合并审计 YAML)
    - *Action*: 
        - **Context-Aware Parsing**: 识别 Markdown 标题 (`##`, `###`) 作为群聊名称，自动路由归档路径。
        - **Full Fidelity Preservation**: 严格保持原文每行内容（含空格、代码块），不做格式转换。
        - **Magic Merge (v2.0 核心算法)**: 
            - **哈希指纹匹配**: 对消息行进行正则预处理 (`RegexPatterns`)，计算 SHA-256 哈希值作为内容指纹。
            - **模糊上下文对齐**: 使用 `seq_match` 算法（步长默认为 5 行）在目标文件中寻找新 Block 的起始和结束锚点。
            - **四种合并模式**:
                - `both_match`: 中间内容智能替换，完美解决导出片段重叠。
                - `begin_match`: 前部对齐，向后补齐缺失消息。
                - `end_match`: 后部对齐，向前补全历史消息。
                - `no_match`: 无重叠点时，按时间戳序列执行物理插入与排序。
        - **Audit Persistence**: 
            - 每一个 Block 都会在 `tasks` 下生成 `dump_{file}_{idx}_raw_chunk.yaml`。
            - 每一个合并操作都会记录 `merge_chunk.yaml`，包含匹配行号、合并类型及前后对比。
    - *Output*: 最终归档结果至 `01` 目录，并更新 `kb/tasks/etl_status.yaml`。
2.  **[Error Handling]**: 如果脚本由于格式或解析问题失败：
    - **[Agent]**: 必须立即根据错误信息（如 `ValueError` 中的行号或内容）执行 `grep` 搜索，定位到原始文件中的具体行。
    - **[Interaction]**: 展示错误行及其上下文，并请用户补充或修正信息。
    - **[Retry]**: 用户修正后重新运行。

## Phase 3: 结果反馈 (Reporting)
1.  **[LLM]**: 阅读 Script 输出的统计信息。
2.  **[Response]**: 向用户汇报。
    - *Template*: "已处理 [文件数] 个原始记录。在 [群组名] 中新增了 [N] 条消息，跳过了 [M] 条重复消息。原始文件已归档至 processed 目录。"
