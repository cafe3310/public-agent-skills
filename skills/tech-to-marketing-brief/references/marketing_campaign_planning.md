# 营销活动与 Brief 规划指南 (Marketing Campaign & Brief Planning)

> 本文档融合了 Claude Plugin 中 `Marketing: campaign-planning` 与 `stakeholder-comms` 的核心工作流。用于指导大模型如何将技术特性转化为标准化的营销 Brief。

## 1. 核心战略推导 (Strategy Formulation)
在生成 Brief 之前，必须先将“技术指标”翻译为“商业与营销价值”：
- **技术映射 (Feature-to-Benefit)**: 
  - *Bad*: “提升了 1M 上下文，支持 CoT 并发推理。”
  - *Good*: “拯救复工信息过载；一个敢于反驳你的毒舌数字参谋。”
- **受众分层 (Audience Segmentation)**: 
  - 针对 KOL/博主：强调“能帮你涨粉的评测模板”。
  - 针对 C端用户：强调“解决你每天最头疼的那个工作痛点”。

## 2. 外部博主 Brief 标准结构 (The Brief Template)
生成的 Brief 必须严格包含以下结构：
1. **背景与北极星目标 (Objective)**: 明确我们这次要打的心智（如：去AI味、最高效的写作分身）。
2. **体验路径与素材 (User Journey)**: 明确的 URL 链接、入口截图说明（如模型切换的下拉框、Thinking 折叠面板的展示要求）。
3. **内容创作指令 (Content Requirements)**: 
   - **核心考题设计**: 必须为博主设计好 1-2 个具体的“极限测试场景”。
   - **禁止项 (Red Lines)**: 明确列出不要做的测试（例如“禁止测写请假条”、“禁止一键生成长文”）。
4. **转化钩子 (Call-To-Action/CTA)**: 粉丝福利、兑换码、或者特定落地页的引导话术。

## 3. 沟通语调 (Stakeholder Comms)
- Brief 最终是由运营人员去向下游供应商派发的。因此，语气要**清晰、结果导向、不讲技术黑话**，像一位资深的营销策划总监。
