# memories-off-declare.md

## 定义的实体类型和关联说明

本 Skill 提取的实体与关系取决于具体任务中的本体定义 Schema（例如 `templates/meta.md`）。它自身并不指定静态的实体类型约束。

## 定义的子过程说明

### "空间初始化"

该子过程用于在开始语料提取前，搭建图谱环境与文件结构。操作编排如下：
1. 初始化 memories-off 知识库：
   `memocli init --path <kg_path> --name <kg_name>`
2. 写入本体元数据规范：
   将 `templates/meta.md` 的内容覆盖写入知识库根目录下的 `meta.md`。
3. 在知识库下创建 `chat_res` 目录并复制重命名原始语料文件。
4. 初始化分片任务清单：
   `python scripts/setup_workspace.py <path_to_chat_res> <task_file_name>.md`

### "提交分片提取结果"

该子过程用于在一个分片（通常为 100 行聊天日志）提取完毕并录入图谱后，执行版本控制变更与提交。操作编排如下：
1. 执行规范的 Git 变更审计与提交：
   `memocli commit --reason "processed chunk <chunk_id>"`
