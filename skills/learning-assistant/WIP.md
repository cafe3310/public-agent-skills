# Work In Progress (WIP)

## 待实现功能：memocli 内容替换/章节更新

当前 `learning-assistant` 的核心设计中，依赖于对 `学习计划` 实体内部特定章节（如 `## 已学习内容` 和 `## 待学习内容`）的动态更新与替换。

**现状：**
目前 `memories-off` (`memocli`) 工具仅支持通过 `append-update` 进行增量追加记录，**尚未实现**对已有文本块或章节的“替换”和“删除”操作。

**临时方案：**
在当前的 `SKILL.md` 系统提示词中，我们通过要求 Agent **“假装存在一个 `memocli update-chapter` 命令”** 来规避这一限制。
例如：
`memocli update-chapter --name "Rust编程-基础语法" --chapter "待学习内容" --content "- 生命周期\n- 借用"`

**下一步计划：**
1. 需要在 `memories-off` 核心工具库中开发并实装真正的 `update-chapter` (或具有类似编辑/替换能力的命令)。
2. 待底层工具支持该能力后，更新本 skill 的 `SKILL.md`，将临时性的文字说明替换为正式的工具使用规范。