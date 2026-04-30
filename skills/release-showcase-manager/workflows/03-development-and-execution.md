# Phase 3: 开发实施 (Development & Execution)

## 目标
基于 Phase 2 规划的任务库，在 `showcases/` 下的独立目录中完成具体的工程实现，同步记录洞察，并遵循视觉规范准备录制环境。

## 操作步骤

1. **任务选取与准备**:
   - 从 `YYYY-MM-DD-HH-comprehensive-demo-backlog.md` 中选取目标任务。
   - 深入阅读关联的 `scenario.md` 和技术维度要求。
2. **环境预热与录制对齐 (Recording Setup)**:
   - **参考规范**: 强制参考 `kb/recording-standards.md`。
   - **检查清单**:
     - [ ] 系统缩放已调至 200%。
     - [ ] 浏览器（如使用）缩放至 125% - 150%。
     - [ ] 清理 UI 噪音（隐藏侧边栏、书签、菜单栏）。
     - [ ] 确认字体符合规范（首选 Inter 或 SF Pro）。
3. **创建独立演示目录 (Isolated Workspace)**:
   - **位置**: 所有演示项目必须存放在 `showcases/` 目录下。
   - **命名规范**: `YYYY-MM-DD-HH-{model}-{category}-{desc}`。
   - 示例路径：`showcases/2026-05-01-14-gemini2-web-react-admin-gen/`。
4. **生成“一页纸”看板 (Project Dashboard)**:
   - 在演示目录下立即生成 `README.md`，包含以下部分以供开发时随时参考：
     - **项目背景**: 模型版本、所属发布周期。
     - **任务目标**: 核心要解决的问题及预期的“Wow Moment”。
     - **工作目录**: 明确当前路径及关联资产路径。
     - **工具栈**: 本次演示涉及的技术、库、以及使用的 Agent Skill（如 `oneshot-website`）。
     - **参考链接**: 链接至 Phase 2 的任务定义、KB 中的叙事模板等。
5. **迭代开发与交互式记录 (Interactive Execution)**:
   - 按照 `LOG.md` 驱动开发。
   - **交互记录点**: Agent 在发现模型局限性或突破性表现时，立即将观察记录至目录下的 `notes.md` 并向用户汇报。
6. **资产关联**:
   - 确保代码、Prompt 模板与记录文档通过文档链接相互关联。
7. **录制准备与演练 (Rehearsal)**:
   - 根据 `README.md` 中的目标，演练操作路径。
   - 确保光标移动符合 `kb/recording-standards.md` 中的“平滑曲线”和“呼吸感停顿”规范。

## 完成标准
- [ ] 演示任务在 `showcases/` 下的独立目录中完成。
- [ ] 录制环境已按 `kb/recording-standards.md` 配置完成。
- [ ] 目录内包含内容详尽的 `README.md` 看板及开发观察笔记（notes.md）。
