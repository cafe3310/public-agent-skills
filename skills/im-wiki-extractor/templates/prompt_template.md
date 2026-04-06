# 子代理提取任务指令

<你的任务>
你要基于以下 `提取规则`，从 `当前的讨论` 这个群聊记录中，提取实体和关系，然后并利用 `memories-off` Agent Skill 的 CLI 工具 `memocli` 将它们添加到知识图谱中。

- 要利用 `此前的讨论` 作为参考，以保持上下文的连贯性；
- 要严格参考 `<工具操作指南>` 中的详细语法来执行提取操作；
- **关键点**: `memocli` 会为实体自动补全 `类型-名称` 前缀（例如：`Member-张三`）。在追加（Append）和建立关系（Relations）时，引用实体名必须包含这个前缀。
- 如果在执行中遇到无法解析的内容或工具报错，必须返回 "ERROR: [原因]"，严禁盲目继续。
- 根据 `最终输出` 的要求，确保在完成所有提取和更新操作后，正确给主 Agent 返回结果状态。
</你的任务>

<提取规则>
{{meta_content}}
</提取规则>

<参考处理步骤>
首先，在 debug_log 目录下创建一个 shell 脚本 `{{kg_path}}/debug_log/process_{{chunk_id}}.sh`，并在其中编写以下命令：

1. **创建实体 (步骤1)**: 
   `cd {{kg_path}} && memocli create-entity --path . --name "名称" --type "类型" --reason "提取自 {{chunk_id}}"`
   *(注意：如果实体已存在，命令会报错，请在脚本中通过 `|| true` 或直接忽略错误继续)*

2. **追加内容 (步骤2)**: 
   `cd {{kg_path}} && memocli append-update --path . --entity "类型-名称" --content "内容摘要 (包含溯源: {{filename}}:{{line_range}})" --reason "提取自 {{chunk_id}}"`
   *(注意：--entity 必须包含类型前缀，不要包含 .md 后缀)*

3. **管理关系 (步骤3)**: 
   `cd {{kg_path}} && memocli manage-relations --path . --source "类型-主实体" --add "谓语:类型-目标实体" --reason "提取自 {{chunk_id}}"`
   *(注意：主实体和目标实体都必须包含类型前缀)*

确保脚本中仅包含 memocli 命令。
然后，执行该脚本并使用 tee 将输出同步记录到 `{{kg_path}}/debug_log/process_{{chunk_id}}.log` 文件中。
然后检查命令执行结果，如果有任何严重错误（非实体已存在错误），记录并返回 "ERROR: [错误信息]"。

4. **编辑 Task (步骤4)**: 
   `sed -i '' 's/\[ \] .*ID: {{chunk_id}}/\[x\] /' {{task_file_path}}` (MacOS 环境)
</参考处理步骤>

<工具操作指南>

### 1. 搜索实体 (Search)
{{help_search}}

### 2. 创建实体 (Create)
{{help_create}}

### 3. 追加内容 (Append)
{{help_append}}

### 4. 管理关系 (Relations)
{{help_relations}}

### 5. 合并实体 (Merge)
{{help_merge}}

---

### 全局执行规则
{{global_rules}}

</工具操作指南>

<最终输出>
如果处理完整并已更新任务清单，返回 "SUCCESS"；否则返回 "ERROR: [原因]"。
</最终输出>

<此前的讨论>
{{context_content}}
</此前的讨论>

<当前的讨论>
{{current_content}}
</当前的讨论>

<当前分片ID>
{{chunk_id}}
</当前分片ID>
