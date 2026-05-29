---
sources:
  - vendor: openai
    repo: openai-cookbook
    path: examples/gpt5/gpt-5_prompting_guide.ipynb
    registry_title: "GPT-5 prompting guide"
    upstream_url: https://github.com/openai/openai-cookbook/blob/main/examples/gpt5/gpt-5_prompting_guide.ipynb
    snapshot_commit: 9b4e6279edd4dceb6b4b7da582482a7c882f7544
    relation: borrows-from
    outline_ref: "[1]"
---

# 📊 评估说明 (Micro-benchmarks)

评估不同文件分隔符在长上下文多文件定位任务中的准确率。

## 评估要点
*   **对比分支**: Compare XML tag delimiters vs Markdown block delimiters.
*   **度量指标**: 定位准确率（Accuracy）、推理时延（Latency）。
*   **评测项目**: 关联至评测任务 [benches/2026-01-01_EXAMPLE-different-delimeter-for-files/](file:///benches/2026-01-01_EXAMPLE-different-delimeter-for-files/)。
