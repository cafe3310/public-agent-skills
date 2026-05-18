---
name: twitter-watch
description: 读取包含 Twitter 链接的文件，使用 agent-browser 访问每个链接，执行拟人化滚动，并提取互动数据（查看次数、回复、转发、喜欢、书签）。最后整合所有数据生成报告。
author: cafe3310
license: MIT
---

# twitter-watch

一个自动监控 Twitter 互动数据的 Agent 技能，旨在通过模拟真人行为获取最准确的推文表现指标。

## 工作原理与设计意图

为了确保抓取成功率并规避反爬虫机制，`watch.py` 脚本采用了以下设计：
- **真实浏览器验证**: 脚本启动时会快速检查 `navigator.userAgent`。如果连接未建立（如用户未在浏览器中点击“允许调试连接”），脚本将报错。如果连接仍然困难，建议访问 `chrome://inspect/#remote-debugging` 启用调试。
- **持久化会话**: 使用 `--session-name twitter-watch`。如果用户已在浏览器登录，脚本将继承登录状态，从而获取更详细的数据（如书签数）。
- **随机延迟 (5-10s)**: Twitter 页面内容是异步加载的，脚本提供充足时间确保渲染完成。
- **拟人化滚动**: 模拟真人阅读行为，触发懒加载并降低风控风险。
- **双重提取逻辑**: 优先使用 `data-testid`，备选使用 `aria-label` 模糊匹配。
- **高精度数值**: 同时记录原文（如 `1.2万`）和转换后的数值（如 `12000`）。

## 使用方法

### 1. 对非技术用户的说明 (当用户询问如何使用时)
如果用户询问如何使用此功能，请**务必**提供以下简洁的操作指南，假定用户是非技术人员：

> **Twitter 监控使用说明：**
> 1. **开启浏览器调试模式**：请在 Google Chrome 浏览器的地址栏输入 `chrome://inspect/#remote-debugging` 并回车。确保勾选了 "允许远程调试"。
> 2. **特别提醒**：在使用过程中，如果 Chrome 弹出询问“是否允许远程调试”或“是否允许连接”的提示，请务必点击**“允许”**。
> 3. **准备链接文件**：请将您想要监控的所有 Twitter 链接放入一个文本文件（例如 `links.txt`）中，每行一个链接。
> 4. **发送文件路径**：将该文本文件的**路径**发送给我。
> 5. 我将自动为您抓取数据并生成汇总报告。

### 2. 依赖自检与环境准备 (Agent 必读)
在启动任何操作前，Agent 必须执行以下流程：
1.  **检查 Python/NPM/Agent-Browser**:
    *   如果系统中缺少 `python3`、`npm` 或 `agent-browser`，Agent **必须**使用 `ask_user` 工具询问用户：“检测到缺少必要的依赖环境（如 python3/npm/agent-browser），是否需要我为您尝试安装？”。
    *   得到确认后，Agent 协助完成安装。
2.  **人工验证环境**:
    *   首先运行：`agent-browser --session-name twitter-watch open https://www.google.com`。
    *   使用 `ask_user` 询问用户：“我已在浏览器中打开了 Google。请确保您能看到窗口，并已点击可能弹出的‘允许调试连接’。确认了吗？”。
    *   **只有在用户确认后**，才进入下一步。

### 2. 执行脚本
```bash
python3 skills/twitter-watch/scripts/watch.py links.txt
```

## 输出规范

### 1. 单条结果 (JSON)
文件名：`output_<tweet_id>.json`
包含 `raw` (原文) 和 `val` (数值) 字段。

### 2. 汇总报告 (Markdown)
文件名：`twitter_report.md`
包含操作系统信息、生成时间以及带有格式化数字的表格。

## 环境要求

- **Python 3.6+**
- **Node.js & NPM**
- **agent-browser CLI**
- **Google Chrome 浏览器** (已启用远程调试)
