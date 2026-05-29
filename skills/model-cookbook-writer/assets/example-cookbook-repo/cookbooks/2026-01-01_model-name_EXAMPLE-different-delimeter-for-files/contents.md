# Compiled Cookbook Contents (EXAMPLE)

本文件由编译脚本自动拼接生成。

<a id="sec-1"></a>
# 第一章：工具调用 (Tool Calling) 最佳实践
本章总结模型在进行复杂工具调用与外部 API 交互时的提示词技巧与编排规范。

<a id="sec-2"></a>
# 第二章：文件分隔符调优技巧
在大模型处理多文件上下文输入时，如何有效分隔文件内容是一个极关键的提示词设计环节。
XML 标签隔离: 推荐使用 `<file name="path/to/file">...</file>` 结构。

## 评估说明 (Micro-benchmarks)
评估不同文件分隔符在长上下文多文件定位任务中的准确率。
度量指标: 定位准确率（Accuracy）、推理时延（Latency）。
评测源码: `benches/2026-01-01_EXAMPLE-different-delimeter-for-files/test_runner.py`

## 代码范例 (Examples)
```python
def format_files_with_xml(files_dict):
    formatted = []
    for filepath, content in files_dict.items():
        formatted.append(f'<file name="{filepath}">\n{content}\n</file>')
    return "\n\n".join(formatted)
```
