# im-local-kb 用户指南

欢迎使用 IM 本地知识库管理工具。本工具旨在帮助你将零散的聊天记录转化为结构化的总结，且所有数据处理均在本地完成，确保隐私安全。

## 快速开始 (Quick Start)

### 第一步：准备数据 (00-chats-input-raw)

1.  打开 IM，找到目标群聊或单聊。
2.  选中需要的聊天记录（可以一次性选中几百条），右键选择“复制”或 `Ctrl+C`。
3.  在 `00-chats-input-raw/` 目录下创建一个 `.md` 文件（文件名随意，建议带日期，如 `raw_20231024.md`）。
4.  **关键格式**：在粘贴的内容中，手动添加一些时间锚点。
    *   格式 1: `-- 2023-10-24` (标准)
    *   格式 2: `-- 10-24 14:30` (带时间)
    *   格式 3: `-- 10-24` (仅日期)
    *   *注意：必须以 `-- ` (两个横杠加空格) 开头。*

    **示例**:
    ```text
    ## -- 群组A

    -- 2023-10-24 10:00
    [张三] ...
    [李四] ...
    ```
5.  如果有图片，请尽量手动保存到 `attachments` 目录并在 Markdown 中引用，或者忽略图片。

### 第二步：清洗与归档 (Ingest)

告诉 Agent：“**帮我处理一下新导入的聊天记录**” 或运行 `normalize_merge` 工具。
*   脚本会自动识别时间锚点，计算哈希去重，并将内容归档到 `01-chats-input-organized/` 目录。
*   **注意**：`01` 目录是机器生成的“标准库”，**请勿手动修改**其中的文件，否则会导致去重失效。

### 第三步：定义项目 (02-project-specs)

在 `02-project-specs/` 目录下创建一个 YAML 文件，用于定义提取任务的边界和目标。

#### 项目定义规范 (Project Spec Specification)

| 字段 | 必填 | 说明 | 可选项/示例 |
| :--- | :--- | :--- | :--- |
| **meta.id** | 是 | 项目唯一标识符，将作为输出目录名 | `proj_model_release_2026_02` |
| **meta.name** | 是 | 项目人类可读名称 | `模型发版工作复盘` |
| **meta.strategy** | 否 | 知识提取策略，默认为 `full` | `full` (全量), `incremental` (增量) |
| **scope.time_range.start** | 是 | 语料扫描的起始日期 | `YYYY-MM-DD` |
| **scope.time_range.end** | 否 | 语料扫描的截止日期 | `YYYY-MM-DD` (缺省为当前日期) |
| **scope.sources** | 是 | 要包含的数据源（群组名）列表 | 对应 `01` 目录下的文件夹名 |
| **sources.name** | 是 | 数据源名称 | `产品_后端架构组` |
| **sources.time_sensitivity** | 否 | 时间敏感度，影响断档检测逻辑 | `high` (强时序), `low` (弱时序) |
| **extraction_goals** | 是 | 提取目标列表 | 至少定义一个目标 |
| **goals.title** | 是 | 目标的简短标题 | `关键风险提取` |
| **goals.prompt** | 是 | 针对该目标的具体 AI 提取指令 | `请识别沟通中提到的所有技术风险...` |

**示例配置 (`proj_sample.yaml`):**
```yaml
meta:
  id: "proj_channel"
  name: "爱好群组追踪"
  strategy: "incremental"  # 仅处理自上次运行以来的新对话

scope:
  time_range:
    start: "2025-12-01"
  sources:
    - name: "群组名"
      time_sensitivity: "low"

extraction_goals:
  - title: "工具推荐"
    prompt: "提取群聊中提到的所有工具、网站或开源项目。"
```

### 第四步：生成报告 (Generate)

告诉 Agent：“**基于 proj_xxx.yaml 生成复盘报告**” 或运行 `extract_knowledge` 工具。
*   Agent 会读取 `01` 中的数据。
*   根据 YAML 中的 `extraction_goals` 提取关键信息。
*   最终报告将生成在 `04-output-documents/` 目录。
*   **提取策略**:
    *   **Full (全量)**: 默认模式。处理所有符合条件的语料。
    *   **Incremental (增量)**: 在 YAML 的 `meta` 中设置 `strategy: "incremental"`。工具将自动计算自上次运行以来新增的语料（`added-contexts.md`），仅对增量进行提取。
    *   *提示：如果没有新语料，增量模式会提示并终止。*
*   **断点续传**: 如果任务因故中断（如 token 超限或网络问题），工具会在 `kb/tasks/` 目录下保存进度。下次运行相同命令时，它会自动从断点处继续，避免重复消耗。

---

## 进阶功能

### 数据完整性检查 (Gap Check)
如果你担心漏掉了某几天的记录，可以告诉 Agent：“**检查一下项目数据的完整性**” 或运行 `analyze_gaps`。
它会扫描 `01` 目录，对比 Project Spec 的时间范围，生成一份 `03-missing-periods` 报告，告诉你哪几天的数据缺失。

### 关于时间戳密度 (Timestamp Density)
为了保证“故障复盘”等强时序任务的准确性，我们在 `normalize` 阶段引入了密度检测。
*   如果你的群聊被标记为 `time_sensitivity: "high"`，但你只在文件开头写了一个 `-- time`，后面粘贴了几千行对话，系统会发出 **警告**。
*   **建议**：对于重要群聊，建议每隔一屏（或话题切换时）就插入一个 `-- time` 标记。

### 增量日志合并 (Incremental Log Merge)
如果你需要将新采集的聊天记录追加到已有的归档文件中，且两份记录存在时间重叠（例如重复了某一天的对话），可以使用 `log_merger.py` 工具。
*   **功能**: 自动识别重叠部分，智能去重并追加新内容。
*   **用法**: 详见 `references/log_merger_usage.md` 指南。
*   **命令示例**: `python scripts/log_merger.py ...` (需指定 `--do-edit` 以生效)。

## 常见问题 (FAQ)

Q: 我可以直接修改 `01` 里的文件吗？
A: 不建议。如果你发现 `01` 里有错别字，建议在 `00` 里修正源文件，然后删除 `01` 里对应的片段（或者清空 `01` 对应文件），重新运行清洗脚本。

Q: 图片怎么处理？
A: 目前建议手动保存关键图片到 `attachments`。全选复制通常只能得到文本。
