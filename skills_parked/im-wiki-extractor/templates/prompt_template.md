# 子代理提取任务指令

<你的任务>
你要基于以下 `提取规则`，从 `当前的讨论` 这个群聊记录中，提取实体和关系，然后并利用 `memories-off` Agent Skill 的 CLI 工具 `memocli` 将它们添加到知识图谱中。

- 要利用 `此前的讨论` 作为参考，以保持上下文的连贯性；
- 要严格参考 `<工具操作指南>` 中的详细语法来执行提取操作；
- **关键点 (命名规范)**: 引用实体名时直接使用其原始名称（例如：`张三`）。**严禁**在实体名前添加 `类型-` 前缀（如 `Member-`）。实体名即文件名。
- 如果在执行中遇到无法解析的内容或工具报错，必须返回 "ERROR: [原因]"，严禁盲目继续。
- 根据 `最终输出` 的要求，确保在完成所有提取和更新操作后，正确给主 Agent 返回结果状态。
</你的任务>

<提取规则>
{{meta_content}}
</提取规则>

<参考处理步骤>
首先，在 debug_log 目录下创建一个 shell 脚本 `{{kg_path}}/debug_log/process_{{chunk_id}}.sh`，并在其中编写以下命令：

1. **高效提取 (推荐模式)**: 
   - **创建并关联**: `cd {{kg_path}} && memocli create-entity -n "名称" -t "类型" [关系参数] -r "提取自 {{chunk_id}}"`
   - **追加并关联**: `cd {{kg_path}} && memocli append-update -e "名称" -c "内容摘要 (包含溯源: {{filename}}:{{line_range}})" [关系参数] -r "提取自 {{chunk_id}}"`

2. **关系参数选择指南 (关键)**:
   - **场景 A：处理概念/观点/话题 (Opinion, Info, Chat等)**
     - 优先使用 `--add-rel-in`。
     - **逻辑**: 将参与讨论的人「拉入」此话题。
     - **示例**: `memocli create-entity -n "观点A" -t "Opinion" --add-rel-in "Propose:张三" --add-rel-in "Support:李四" --add-rel-in "Discuss:王五,赵六"` (表示张三提出、李四支持、王五和赵六也参与了该观点讨论)。
   - **场景 B：处理成员 (Member)**
     - 优先使用 `--add-rel-out`。
     - **逻辑**: 记录该成员「发出」的动作。
     - **示例**: `memocli append-update -e "张三" -c "展现了...素养" --add-rel-out "Manifest:领域-知识" --add-rel-out "Support:观点B" -r "..."`。

3. **注意事项**:
   - 如果实体已存在，`create-entity` 会报错，请通过 `|| true` 忽略。
   - 所有的 `-e` 或 `-n` 参数仅包含实体名称，**严禁**包含类型前缀。
   - 关系参数支持**多次调用**（用于不同谓语或目标集）以及**逗号分隔**（用于同一谓语的多个目标）。
   - 每个提取出的实体，必须至少通过一个关系参数（通常是 `Propose` 或 `Repost`）与发言人关联。

确保脚本中仅包含 memocli 命令。
然后，执行该脚本并使用 tee 将输出同步记录到 `{{kg_path}}/debug_log/process_{{chunk_id}}.log` 文件中。
然后检查命令执行结果，如果有任何严重错误（非实体已存在错误），记录并返回 "ERROR: [错误信息]"。

3. **标记进度**: 
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
