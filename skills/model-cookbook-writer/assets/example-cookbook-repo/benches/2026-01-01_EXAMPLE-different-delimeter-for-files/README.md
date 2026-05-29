---
sources:
  - vendor: openai
    repo: openai-cookbook
    path: examples/gpt5/gpt-5_prompting_guide.ipynb
    registry_title: "GPT-5 prompting guide"
    upstream_url: https://github.com/openai/openai-cookbook/blob/main/examples/gpt5/gpt-5_prompting_guide.ipynb
    snapshot_commit: 9b4e6279edd4dceb6b4b7da582482a7c882f7544
    relation: benchmarks-against
    outline_ref: "[1]"
    note: "本 bench 作为对照评估 GPT-5 推荐分隔符在目标模型上的命中差异。"
---

# Micro-benchmark: 不同文件分隔符表现对比

## 1. 评测目的
测试当输入中包含多个文件时，模型能否准确理解各文件的独立边界，避免上下文混淆或串线。

## 2. 评测方式
向模型输入 5 个文件内容（部分包含重名变量或相似结构），向其提问特定文件中的核心逻辑，验证模型是否能定位并准确抽取。

## 3. 对比方案
- **方案 A (XML Tag)**: 使用 `<file name="...">...</file>` 包裹文件。
- **方案 B (Markdown Block)**: 使用 `### File: ...` 及 ` ```python ` 代码块分隔。

## 4. 判定标准 (Rubrics)
- **正确 (Correct)**: 模型回答仅引用了指定文件中的值，且未受其他同名变量混淆。
- **混淆 (Confused)**: 模型回答混淆了其他文件的内容，或回答“未找到”。
