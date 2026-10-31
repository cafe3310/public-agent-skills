# Workflow: Gap Analysis

## 核心工具
- **SCRIPT_init_validate.py**: 前置校验，检查结构。
- **SCRIPT_analyze_gaps.py**: 基于 `02` 的定义，检查 `01` 中是否存在时间断档。
    - **Args**: `--spec-file kb/02-project-specs/proj_NAME.yaml --data-dir kb/01-chats-input-organized --output-dir kb/03-missing-periods`

## Phase 1: 解析需求 (Spec Parsing)
1.  **[Script]**: 调用 `SCRIPT_init_validate.py` 验证知识库完整性。
2.  **[Script]**: 调用 `SCRIPT_analyze_gaps.py`。
    - *Input*: `02-project-specs/proj_xxx.yaml`
    - *State Check*: 读取 `kb/tasks/etl_status.yaml` 获取数据覆盖范围 (Effective Range)。
    - *Action*: 
        - 提取 `start_date`, `end_date`, `sources`。
        - 扫描 `01` 中对应群组的时间轴。
        - 识别超过阈值（如 >3天）的空白期。
        - **Coverage Check**: 区分 "静默 (Silent)" 和 "缺失 (Missing)"。
    - *Output*: 生成 `03-missing-periods/{project_id}/{timestamp}.yaml`。

## Phase 2: 智能解读 (Interpretation)
1.  **[LLM]**: 读取生成的 `03` YAML 文件。
2.  **[Thinking]**: 
    - 缺失的时间段是否在周末或节假日？（LLM 内置知识库判断）
    - 缺失的数据量是否致命？（例如：缺了上线当天的记录 vs 缺了平时的记录）
3.  **[Response]**: 生成自然语言建议。
    - *Example*: "项目定义范围是 10月。目前 [架构群] 数据完整，但 [指挥部] 缺少 10月1日-7日 的记录。如果是国庆假期可忽略，否则建议补充采集。"
    - *Action Item*: "请手动去 IM 复制该时间段消息，放入 00 目录，然后重新运行 Ingest。"
