# Phase 5: 评价与洞察 (Evaluation & Insights)

## 目标
产出正式的模型评价文档与运营 Brief，整合开发过程中的所有笔记，为发布提供具备实战数据支撑的技术背书。

## 操作步骤

1. **多源笔记汇总 (Note Integration)**:
   - 深度汇总根目录下 `notes/` 以及各个 `showcases/{dir}/notes.md` 中的记录。
   - 整理开发过程中所有交互式记录的“闪光点”与“翻车现场”。
2. **调用评价标准 (Standard Reference)**:
   - 强制参考 `kb/model-brief-standard.md`。
   - 确保产出文档包含核心价值、运营 Brief、KOL 建议、陷阱表格及案例组合。
3. **编写评价底稿 (Drafting the Brief)**:
   - **命名规范**: `YYYY-MM-DD-HH-model-{model_name}-{version}-evaluation.md`。
   - 遵循标准中的 8 个核心章节进行撰写。
4. **多维度评价与打分 (Scoring)**:
   - 结合 Phase 2 的图谱维度进行打分（1-10）：
     - 逻辑推理与任务规划
     - 指令遵循与风格对齐
     - 代码生成与工程修复
     - UI 审美与布局完成度
     - 鲁棒性与一致性
5. **亮点与不足 (Highlights & Bottlenecks)**:
   - 显式列出本次 Showcase 中模型最惊艳的 3 个“决定性瞬间”。
   - 诚实记录模型在开发中遇到的主要瓶颈及建议的工程化规避方案。
6. **沉淀提示词资产**:
   - 将验证有效的系统提示词和 Few-shot 样本记录至底稿。

## 完成标准
- [ ] 已产出符合 `kb/model-brief-standard.md` 标准的正式评价底稿。
- [ ] 底稿已深度整合所有开发笔记，包含具体的量化评分与亮点分析。
- [ ] 文档遵循 `YYYY-MM-DD-HH-` 命名规范。
