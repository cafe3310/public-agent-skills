# Subcommand: `/guide load` (环境感知与项目上下文加载)

## 1. 核心意图与定位

`/guide load` 是新 Session 启动、上下文重置或交接后的**首要环境与架构感知指令**，等同于用户明确指示：
> **“你先读取 guide skill 的主 skill.md，然后确保你了解：最近的两三个 backlog、handoff.md 和近期的几个 commit、未 commit 的内容（项目最近发生的事情）；也了解：项目 agents.md 和其要求的整体架构、项目 agents.md 要求了解的其他 skill、项目的模块分布、spec 目录下的要求（仅文件名就好）（项目的整体结构和规约）；然后简单汇报。”**

---

## 2. 标准执行步骤

### 步骤 0：确认主 Skill 规则
- 快速查阅 `skills/guide/SKILL.md`，确认项目的默认路径约定（文档目录、TODO 路径、子命令用法）。

### 步骤 1：感知项目最近发生的事情 (Recent Project Context)
1. **最近的 2～3 个 Backlog**：
   - 查阅 `{文档目录}/`（如 `docs/` 或 `backlog/`）下最新创建的 2～3 篇开发日志或设计文档，了解上几次任务的具体改动与排查成果；
2. **`HANDOFF.md` 与近期 Git Commits**：
   - 检查项目根目录下是否存在 `HANDOFF.md`，若有则读取其工程目标与避坑提示；
   - 运行 `git log -n 5 --oneline` 快速掌握近期几次代码提交脉络；
3. **未 Commit 的工作区现状**：
   - 运行 `git status -s` 检查当前是否有正在编辑中、未提交的暂存/工作区代码。

### 步骤 2：掌握项目的整体结构和规约 (Architecture & Specifications)
1. **`AGENTS.md` 及其架构要求**：
   - 读取项目根目录下的 `AGENTS.md`，明确项目背景意图、核心技术栈与整体架构要求；
2. **`AGENTS.md` 要求的其他 Skill**：
   - 识别项目中被明确要求的其他 Agent Skill（例如 UI 规范工具 `impeccable`、现代 Web 规范 `modern-web-guidance` 等），并在后续对应任务中遵循；
3. **项目的模块分布**：
   - 快速浏览代码根目录（如 `src/`）的主要子目录结构，了解业务页面、后端服务、共享契约、底层数据层的物理分布；
4. **Spec 目录下的要求（仅浏览文件名）**：
   - 列出 `{文档目录}/specifications/`（或 `specification/`）目录下的所有规范文件名；
   - **轻量原则**：此时仅需了解有哪些长期 Spec 存在（建立目录索引），**无需提前深读所有正文**，等到具体任务触发时再按需深入查阅。

### 步骤 3：向用户简单汇报

汇报保持直接、克制、结构化，例如：

```markdown
### 🎯 项目架构与环境感知就绪

- **最近动态**：
  - 最近 Backlog：`[XXXX-开发日志-...]`、`[XXXX-设计-...]`
  - 存在 HANDOFF 交接（焦点：...） / 近期提交：`feat: ...`
  - 工作区状态：干净 / 有 X 个未提交修改
- **架构与规约**：
  - 项目定位：[简述]；遵循 Skill：`guide`, `impeccable` 等
  - 模块分布：`shared` 契约 / `main` 服务 / `renderer` 视图
  - 已挂载 Spec 列表：`01-module-boundaries`, `02-type-system`, `03-development-paradigms`, `04-logging`
- **准备就绪**：请指示下一步任务。
```
