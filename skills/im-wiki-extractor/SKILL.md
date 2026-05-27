---
name: im-wiki-extractor
description: 专门用于将超长群聊日志转化为结构化知识图谱。采用滑动窗口增量提取，规避上下文限制，并确保实体与关系的沉淀与溯源。
license: Apache-2.0
author: github/cafe3310
depends_on_skill:
  - github/cafe3310/agent-skill-memories-off -> memories-off
depends_on_binary:
  - python3
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
1. **自动定位**: 启动任务时，直接定位到 `TASK` 文件中第一个 `[ ]` 状态的分片开始处理。
2. **生成提示词**: 运行 `python scripts/generate_prompt.py ...`。该脚本现在会动态注入支持「组合操作」的 `memocli` 语法（如在追加内容的同时建立关系）。
3. **执行提取子任务 (原子化操作)**:
    - **组合指令优先**: 优先使用 `append-update --add-rel-out` 等组合指令，减少工具调用次数。
    - **路径自动探测**: 默认在知识库根目录执行，无需显式传入 `--path`。
    - **失败处理**: 若执行中断，直接在下一次尝试时重新处理该分片。
4. **记录与提交**:
    - 检查 `TASK` 文件，确认分片状态已更新为 `[x]`。
    - **标准化提交**: 执行 `memocli commit -r "processed chunk [ID]"`。该命令会自动触发全库审计并生成标准的 Git 提交信息。
5. **检查并继续**: 进入下一个分片。

## 4. 执行原则 (Execution Principles)

- **命名规范 (Identity)**: 实体名即文件名。严禁添加类型前缀。
- **组合语义 (Combined Ops)**: 充分利用 `memocli` 的 `--add-rel-out/in` 参数。在 `create-entity` 或 `append-update` 时同步完成关系建模，提升提取效率。
- **动态语法核验**: `generate_prompt.py` 会实时调用 `memocli --help` 以确保子代理使用的语法与当前环境安装的版本 100% 匹配。
- **最小化探测**: 
    - 识别到实体后直接 `create-entity`，通过 `|| true` 忽略已存在错误。
    - 严禁冗余的 `ls` 或全局 `search`。
- **溯源强制**: 所有的 `append-update` 必须包含 `filename:line_range`。

## 5. 资源清单 (Resources)

### 脚本 (Scripts)
- `scripts/setup_workspace.py`: 初始化分片任务清单。
- `scripts/generate_prompt.py`: 动态组装包含权威 CLI 语法的子代理提示词。

### 模板 (Templates)
- `templates/prompt_template.md`: 核心任务模板，包含元数据和工具操作占位符。
- `templates/meta.md`: 图谱本体定义模板。
