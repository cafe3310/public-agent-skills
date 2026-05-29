---
title: 文件分隔符调优技巧
sources:
  - vendor: openai
    repo: openai-cookbook
    path: examples/gpt5/gpt-5_prompting_guide.ipynb
    registry_title: "GPT-5 prompting guide"
    upstream_url: https://github.com/openai/openai-cookbook/blob/main/examples/gpt5/gpt-5_prompting_guide.ipynb
    snapshot_commit: 9b4e6279edd4dceb6b4b7da582482a7c882f7544
    relation: borrows-from
    outline_ref: "[1]"
    note: "示例引用 —— 实际工程中按 SKILL.md §4 SourceRef 契约填写真实条目。"
---

# 📄 第二章：文件分隔符调优技巧

在大模型处理多文件上下文输入时，如何有效分隔文件内容是一个极关键的提示词设计环节。

## 技巧要点
1.  **XML 标签隔离**: 推荐使用 `<file name="path/to/file">...</file>` 结构，这相比传统的 Markdown 代码块有更好的抗混淆能力。
2.  **避免转义冲突**: 如果文件内容本身包含 XML 标签，应使用 CDATA 或三反引号（```）对内层进行物理包裹。
