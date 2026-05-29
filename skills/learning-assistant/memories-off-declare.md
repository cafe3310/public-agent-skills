# memories-off-declare.md

## 定义的实体类型和关联说明

本 Skill 依赖 `memories-off` 库，在知识图谱中维护以下五类实体以追踪用户学习进度。所有实体的 H2 章节结构、命名规范以及创建/更新命令必须严格遵循以下定义：

### 1. 当前学习状态
- **实体名称**：`当前学习状态` (全局唯一)
- **说明**：记录当前正在学习的主题和计划。必须且仅能包含 `## 当前正在进行的主题`、`## 当前正在进行的计划` 和 `## 当前正在介绍的概念` 三个标准 H2 章节以框定核心格式。不与任何其他实体建立显式关系。
- **创建并初始化**：
  ```bash
  echo -e "## 当前正在进行的主题\n无\n\n## 当前正在进行的计划\n无\n\n## 当前正在介绍的概念\n无" | memocli create-entity --name "当前学习状态" --type "状态" --content-stdin --reason "初始化当前学习状态"
  ```
- **状态更新**：必须使用 `memocli update-chapter` 命令针对指定章节进行精确覆盖更新。例如：
  ```bash
  echo "Rust编程" | memocli update-chapter --entity "当前学习状态" --chapter "当前正在进行的主题" --content-stdin --reason "切入新主题"
  ```
- **实例参考**：[当前学习状态.md](./example_kb/entities/当前学习状态.md)

### 2. 学习日志
- **实体名称**：`学习日志-{YYYYMMDD}` (如 `学习日志-20260518`)
- **说明**：用于记录重要进度变更、阶段成果或每日交互，不与其他实体建立显式关系。
- **创建**：
  ```bash
  memocli create-entity --name "学习日志-20260518" --type "学习日志" --reason "创建每日学习日志"
  ```
- **更新方式**：使用 `memocli append-update` 命令以非破坏性的增量追加形式记录日志内容。例如：
  ```bash
  echo "- 20:30 完成了 Zig 看板 of DOM ID Bug 修复与调试工作" | memocli append-update --entity "学习日志-20260602" --content-stdin --reason "追加今日学习记录"
  ```
- **实例参考**：[学习日志-20260602.md](./example_kb/entities/学习日志-20260602.md)

### 3. 学习主题
- **实体名称**：`{主题名称}` (例如 `Rust编程`)
- **说明**：表示想要学习的一个完整、高阶的知识领域。
- **创建**：
  ```bash
  memocli create-entity --name "Rust编程" --type "学习主题" --reason "规划新学习主题"
  ```
- **实例参考**：[微服务架构.md](./example_kb/entities/微服务架构.md)

### 4. 学习计划
- **实体名称**：`{主题名称}-{计划名称}` (例如 `Rust编程-基础语法`)
- **说明**：针对某个主题的具体、可执行的学习路径。必须且仅能包含 `## 参考资料`、`## 已学习内容` 和 `## 待学习内容` 三个标准 H2 章节以框定其结构，禁止随意更改。
- **关系关联**：学习计划 `--BELONGS_TO-->` 学习主题。
- **创建并初始化**：
  ```bash
  echo -e "## 参考资料\n无\n\n## 已学习内容\n无\n\n## 待学习内容\n- 概念1\n- 概念2" | memocli create-entity --name "Rust编程-基础语法" --type "学习计划" --add-rel-out "BELONGS_TO:Rust编程" --content-stdin --reason "初始化学习计划"
  ```
- **内容更新**：必须严格遵循**先读后写**原则。在更新前，应先通过 `memocli get-chapter` 读取当前章节的完整内容（由于学习计划通常不长，也可以直接读取整个实体），在确认需要修改的部分后，再使用 `memocli update-chapter` 命令对指定 H2 章节进行就地覆盖更新。
  例如：
  1. 先读取章节：
     ```bash
     memocli get-chapter --entity "Rust编程-基础语法" --chapter "待学习内容"
     ```
  2. 修改后覆写：
     ```bash
     memocli update-chapter --entity "Rust编程-基础语法" --chapter "待学习内容" --content "- 生命周期\n- 借用" --reason "更新待学习内容"
     ```
- **实例参考**：[微服务架构-Docker基础.md](./example_kb/entities/微服务架构-Docker基础.md)

### 5. 概念
- **实体名称**：`{主题名称}-{计划名称}-{概念名称}` (例如 `Rust编程-基础语法-所有权`)
- **说明**：独立的知识点或方法，学习的基本单元。必须且仅能包含 `## 概念详解` 和 `## 学习过程整理` 两个标准 H2 章节以框定其结构。
- **关系关联**：概念 `--BELONGS_TO-->` 学习计划。
- **创建并初始化**：
  ```bash
  echo -e "## 概念详解\n(在此处输入概念的基础描述...)\n\n## 学习过程整理\n无" | memocli create-entity --name "Rust编程-基础语法-所有权" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法" --content-stdin --reason "初始化概念"
  ```
- **过程更新**：在介绍完概念、用户问答结束、即将前往下一个概念时，必须使用 `memocli update-chapter` 对 `## 学习过程整理` 章节进行精确覆盖和总结。
- **实例参考**：[微服务架构-Docker基础-镜像与容器.md](./example_kb/entities/微服务架构-Docker基础-镜像与容器.md)

---

## 关系关联汇总说明

- `[[学习计划]]` BELONGS_TO `[[学习主题]]`
- `[[概念]]` BELONGS_TO `[[学习计划]]`

---

## 定义的子过程说明

### "恢复学习状态"

在每次对话恢复时，用于找回上一次的学习上下文进度。操作编排如下：
1. 读取全局学习状态实体：
   `memocli load-entities --names "当前学习状态"`
2. 若实体不存在，则冷启动创建它：
   `memocli create-entity --name "当前学习状态" --type "状态" --reason "初始化恢复学习状态"`

### "规划新学习主题"

当开始新的主题领域学习时，用于批量创建整个图谱网络。操作编排如下：
1. 创建学习主题：
   `memocli create-entity --name "<主题名称>" --type "学习主题" --reason "规划新主题"`
2. 创建对应的学习计划，写入待学习章节：
   `memocli create-entity --name "<主题名称>-<计划名称>" --type "学习计划" --reason "规划新计划"`
3. 批量为每一个划分的概念创建实体并建立 `BELONGS_TO` 关联：
   `memocli create-entity --name "<主题名称>-<计划名称>-<概念名称>" --type "概念" --add-rel-out "BELONGS_TO:<主题名称>-<计划名称>" --reason "建立概念点"`
4. 修改全局学习状态：
   `echo "当前正在进行主题：<主题名称>，计划：<计划名称>" | memocli append-update --entity "当前学习状态" --reason "更新当前学习状态"`
5. 创建当天学习日志：
   `memocli create-entity --name "学习日志-<当前日期>" --type "学习日志" --reason "新建规划日志"`
   *(提示：在运行上述命令时，若已经配置了全局别名配置，建议附加 `-p <alias>` 别名简化路径参数操作).*
