# Workflow: Knowledge Base Backup

## 概述
提供对知识库目录 (`kb/`) 的全量防御性备份功能。建议在执行任何数据合并或结构调整前运行。

## 核心脚本
- **脚本**: `SCRIPT_backup_full.py`
- **功能**: 执行全量备份，生成带时间戳的 ZIP 压缩包。
- **参数**:
    - `--source kb`: 备份源目录 (指向 `kb` 目录)
    - `--dest kb/backups`: 备份存放目录 (指向 `kb/backups` 目录)
