# Bench Results: 不同文件分隔符表现对比

## 1. 评测背景
- **评测项目**: [benches/2026-01-01_EXAMPLE-different-delimeter-for-files/](file:///benches/2026-01-01_EXAMPLE-different-delimeter-for-files/)
- **测试模型**: `model-name`

## 2. 结论摘要
XML 分隔符相比 Markdown 原始分隔符展示出显著的边界防混淆优势，准确率高出 13%。

## 3. 跑分指标
- XML 分隔符准确率: 95.0%
- Markdown 分隔符准确率: 82.0%

## 4. 复现步骤
```bash
python3 benches/2026-01-01_EXAMPLE-different-delimeter-for-files/test_runner.py
```
