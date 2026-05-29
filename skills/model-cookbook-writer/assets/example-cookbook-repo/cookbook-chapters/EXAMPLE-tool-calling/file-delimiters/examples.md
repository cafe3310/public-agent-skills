---
sources: []   # 示例：原创推导，无第三方借鉴。实际工程中按 SKILL.md §4 SourceRef 契约填写。
---

# 💡 代码范例 (Examples)

以下是用于将多文件组装并添加 XML 分隔符的 Python 代码样例：

```python
def format_files_with_xml(files_dict):
    formatted = []
    for filepath, content in files_dict.items():
        formatted.append(f'<file name="{filepath}">\n{content}\n</file>')
    return "\n\n".join(formatted)

# 示例输入
files = {
    "src/main.py": "print('hello')",
    "README.md": "# Title"
}
print(format_files_with_xml(files))
```
