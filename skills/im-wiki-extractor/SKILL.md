---
name: im-wiki-extractor
description: 专门用于将超长群聊日志转化为结构化知识图谱。采用滑动窗口增量提取，规避上下文限制，并确保实体与关系的沉淀与溯源。
author: github/cafe3310
license: Apache-2.0
---

# Agent Skill: im-wiki-extractor (群聊知识图谱提取器)

## 1. 概述 (Overview)

本技能旨在将非结构化的聊天记录（如群聊历史）转化为存储在 `memories-off` Agent Skill 生成的仓库中的结构化知识图谱。
它强调「逐渐增量」的处理方式，通过 100 行一个的「滑动窗口」来处理超长日志，从而规避模型上下文限制。
该技能通过动态注入工具的 `help` 信息来确保子代理生成 100% 正确的 CLI 指令。

## 2. 提取定义 (Schema)

提取任务应遵循用户给出的实体和关系规范。
在 `templates/meta.md` 中包含了一个示例定义，定义了实体的类型（Member, Opinion, Info 等）及其关系谓语（Propose, Discuss 等）。
用户可以根据实际需求进行调整。

## 3. 工作流阶段 (Workflow Phases)

### 第一阶段：准备与访谈
1. **确认范围**: 询问语料位置及目标知识库目录。
2. **Schema 确认**: 引导用户确认 `templates/meta.md`。
3. **目标定义**: 确认 `templates/prompt_template.md`。

### 第二阶段：空间初始化
1. **初始化 `memories-off` 仓库**: 在用户指定的地方创建知识目录并执行 `memocli init`。
2. **配置元数据**: 用 cp 命令将 `templates/meta.md` 的内容写入知识库的 `meta.md`；或根据用户之前的输入动态生成 `meta.md`。
3. **复制语料**: 在 `memocli init` 创建的知识库中创建 `chat_res` 子目录，用于存储规范化后的原始语料；然后将原始日志复制到 `chat_res`，按顺序重命名为 `YYYY-MM-DD_NNN_orig_name.md`。
5. **任务分解与状态追踪**: 运行 `python scripts/setup_workspace.py path_to_chat_res TASK_YYYY-MM-DD.md`。该脚本会扫描语料并生成带有行号分片（100行）和前序上下文（50行）的 `TASK` 文件。

### 第三阶段：增量提取循环 (断点续传)
针对 `TASK` 文件中定义的每个未完成分片（`[ ]`）：
1. **自动定位**: 任何时候启动任务，都必须直接定位到 `TASK` 文件中第一个 `[ ]` 状态的分片，直接开始处理。禁止对 `chat_res` 目录下的原始大文件进行全量读取或关键词扫描。
2. **生成提示词**: 运行 `python scripts/generate_prompt.py templates/prompt_template.md chat_res [知识库路径] [TASK文件路径] "[任务行内容]"` 来生成子代理所需的完整提示词。该脚本只会读取必要的行范围。
3. **执行提取子任务 (原子化操作)**:
    - 将生成的提示词发送给子代理（建议使用 `generalist`）。
    - 子代理会根据提示词从分片中提取实体和关系，并利用 `memocli` 更新图谱。
    - **失败处理**: 如果子代理执行失败或中断，无需进行状态恢复，直接在下一次尝试时重新处理该分片。
    - 子代理执行完成后，必须更新 `TASK` 文件中的分片状态（标记为已完成 `[x]`）和提取结果的来源信息。
4. **记录与提交**:
    - 检查 `TASK` 文件，确认分片状态已更新。
    - 执行 Git commit，提交信息必须包含分片 ID（例如：`feat: processed chunk 2026-04-06_1-100`）。
5. **检查并继续**: 进入下一个分片。

## 4. 执行原则 (Execution Principles)

- **命名规范 (Identity)**: 严格遵守「实体名即文件名」的约定。在 `append-update` 和 `manage-relations` 中，直接使用实体的原始名称作为标识，**严禁添加任何类型前缀**（如不再使用 `Member-张三`，仅使用 `张三`）。
- **动态语法核验**: 所有的提示词生成必须依赖 `generate_prompt.py`，它会通过实时调用 `memocli --help` 来消除指令版本偏差。
- **强制上下文连贯**: 处理分片时必须传入上一分片的结尾（作为 `此前的讨论`），以保持实体识别的连续性。
- **最小化探测**: 
    - 识别到实体后直接 `create-entity`。
    - 报错「实体已存在」是正常现象，忽略错误并继续 `append-update` 即可。
    - 严禁冗余的 `ls` 或全局 `search`。
- **溯源强制**: 所有的 `append-update` 必须包含来源文件和行号。

## 5. 资源清单 (Resources)

### 脚本 (Scripts)
- `scripts/setup_workspace.py`: 初始化分片任务清单。
- `scripts/generate_prompt.py`: 动态组装包含权威 CLI 语法的子代理提示词。

### 模板 (Templates)
- `templates/prompt_template.md`: 核心任务模板，包含元数据和工具操作占位符。
- `templates/meta.md`: 图谱本体定义模板。
