---
name: twitter-watch
description: 读取包含 Twitter 链接的文件，使用 agent-browser 访问每个链接，执行拟人化滚动，并提取互动数据（查看次数、回复、转发、喜欢、书签）。最后整合所有数据生成报告。
license: MIT
author: github/cafe3310
depends_on_skill:
  - github/cafe3310/public-agent-skills -> agent-browser
depends_on_binary:
  - python3
  - node
  - npm
---

# twitter-watch

一个自动监控 Twitter 互动数据的 Agent 技能，旨在通过模拟真人行为获取最准确的推文表现指标。

## 工作原理与设计意图

为了确保抓取成功率并规避反爬虫机制，`watch.py` 脚本采用了以下设计：
- **自动配置**: 脚本启动时会自动检查并确保 `~/.agent-browser/config.json` 中配置了 `{"autoConnect": true}`，这确保了 agent-browser 优先尝试连接用户已打开的真实浏览器。
- **强制有头模式**: 所有命令均附带 `--headed` 参数，确保浏览器界面可见，方便用户监控和必要时介入（如处理验证码）。
- **真实浏览器验证**: 脚本会检查 `navigator.userAgent`。如果仍处于 `Headless` 模式或未建立连接，脚本将发出警示。
- **持久化会话**: 使用 `--session-name twitter-watch`。如果用户已在浏览器登录，脚本将继承登录状态。
- **拟人化滚动与随机延迟**: 模拟真实用户行为，触发推文动态加载。

## 使用方法

### 1. 对非技术用户的说明 (当用户询问如何使用时)
如果用户询问如何使用此功能，请**务必**提供以下简洁的操作指南：

> **Twitter 监控使用说明：**
> 1. **开启浏览器调试模式**：在 Chrome 地址栏输入 `chrome://inspect/#remote-debugging` 并回车，确保勾选 "允许远程调试"。
> 2. **准备环境**：脚本会自动为您配置 `agent-browser`。在使用过程中，如果 Chrome 弹出“是否允许远程调试”提示，请务必点击**“允许”**。
> 3. **准备链接文件**：将想要监控的 Twitter 链接放入文本文件（如 `links.txt`），每行一个。
> 4. **发送文件路径**：将文件路径发送给我，我将自动抓取数据并生成 `twitter_report.md` 报告。

### 2. 执行流程 (Agent 必读)
1. **环境准备**: 确保已安装 `agent-browser` 和 `python3`。
2. **人工验证**: 
   * 首先运行：`agent-browser --headed --session-name twitter-watch open https://www.google.com`。
   * 使用 `ask_user` 确认用户已看到窗口并允许连接。
3. **启动监控**:
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
