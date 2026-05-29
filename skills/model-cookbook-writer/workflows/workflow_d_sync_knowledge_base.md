# 工作流 D: 知识图谱与文档同步 (Knowledge Base & Vault Synchronization)

本工作流规范了在阶段性开发完成后，如何将交付成果及进展记录至 Obsidian 个人知识库与 `memocli` 本地知识图谱，实现”代码库”与”知识库”的联动。

---

## 1. 执行步骤

### 步骤 1: 知识图谱探索与非破坏性追加 (memocli)
- **触发**: 阶段性评测数据产生或 Cookbook 项目编译交付后。
- **行动**:
  1. **结构探索**: 在操作前，必须先在终端执行 `memocli explore` 或相关查询，以理解目标实体的已有关系与属性。
  2. **非破坏性追加**: 使用 `memocli` 的更新命令，以非破坏性的缓冲更新块 (Buffer-Update 模式) 将新跑分结论、大纲变更、Cookbook 版本等数据追加至对应实体中。**禁止直接覆写或破坏该实体中已有的其他历史关联。**

### 步骤 1.5: Obsidian 文档读取（memocli 读路径）
- **触发**: 需要参考 Obsidian 端某份大纲源档、知识 note、历史开发日志作为本次开发输入时。
- **行动**:
  1. **按名找文档**: `memocli find-doc-by-name <关键词或精确名>` 用于在 Obsidian vault 中按文件名模糊 / 精确定位 `.md` 文档，返回候选清单。
  2. **读文档内容**: `memocli read-doc-by-name <精确文件名>` 拉取目标 markdown 文档全文内容，作为本次开发的上下文输入。
  3. **可选实体细化**: 若需要更深层级的实体关系，调用 `memocli load-entities` 与 `memocli get-relations <entity>` 配合，将「文档级」与「图谱级」信息互补使用。
- **规范**: 写路径（步骤 1）与读路径（本步）形成完整闭环；读取的文档若涉及版本变化（如大纲新增章节），应在写路径中同步反向更新。

### 步骤 2: Obsidian 状态文档创建 (cafe3310-obsidian-writer)
- **触发**: 在 Obsidian 笔记库（根目录）中建立动态的工作追踪日志。
- **命名规范**: `YYYY-MM-DD-HH-mm-工作状态-{项目简述}.md` (使用 `date` 命令获取精确时间)。
- **行动**:
  1. **配置 Frontmatter**:
     ```yaml
     ---
     title: "YYYY-MM-DD-HH-mm 📅 - {项目名}工作状态"
     date created: "YYYY-MM-DD-HH-mm"
     date modified: "YYYY-MM-DD-HH-mm"
     ---
     ```
  2. **写入首节生成说明 (强制契约)**:
     ```markdown
     ## 文档生成说明
     
     本文档由 model-cookbook-writer 技能生成。生成原因是记录 {项目名称} 阶段性开发进展。
     
     参考来源:
     - 知识库: {关联实体名称}
     - [[{Obsidian大纲源档名}]]
     ```
  3. **标注项目与性质标签**:
     在生成说明下方空一行，标注项目专属标签，如：
     `#Type-规划 #Project-<项目标签>`
  4. **正文列表记录**:
     - 使用无序列表记录本阶段的进展，优先使用 `🟩` 标示已完成的工作，使用 `🟥` 标示遗留或待项目负责人决断的问题。

### 步骤 3: iCloud 级 Git 提交与同步优化
- **触发**: 当两个仓库（代码库与 Obsidian 库）的修改都落盘后。
- **行动**:
  1. 检查并确保两库的 Git 配置已启用 iCloud 防御优化：
     ```bash
     git config gc.auto 50
     git config gc.autoDetach false
     git config gc.autoPackLimit 10
     git config transfer.unpackLimit 1
     ```
  2. 在两库分别执行：
     ```bash
     git add .
     git commit -m "docs: sync cookbook milestone YYYY-MM-DD"
     git gc # 强制前台打包 loose objects，防止 iCloud 冲突
     ```

---

## 2. 约束规范

- **溯源声明**: Obsidian 中新建的所有记录文档，顶部必须显式且准确地挂载图谱实体（格式如 `- 知识库: 实体名`）及大纲源档的文件 WikiLink。
- **安全提交**: 在 iCloud 目录中操作 Git 时，绝对禁止后台执行 `git gc`，必须使用前台阻塞模式，以确保打包过程不会因 iCloud 云端拉取同步而发生文件锁死或损坏。
