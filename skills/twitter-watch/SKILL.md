---
name: twitter-watch
description: 读取包含 Twitter 链接的文件，使用 agent-browser 访问每个链接，执行拟人化滚动，并提取互动数据（查看次数、回复、转发、喜欢、书签）。最后整合所有数据生成报告。
author: cafe3310
license: MIT
---

# twitter-watch

一个自动监控 Twitter 互动数据的 Agent 技能。

## 使用方法

1. 准备一个文本文件（例如 `links.txt`），每行包含一个 Twitter URL。
2. 运行监控脚本：

```bash
python3 skills/twitter-watch/scripts/watch.py links.txt
```

## 工作原理

`watch.py` 脚本会对每个 URL 执行以下操作：
1. **打开**: 使用 `agent-browser` 配合持久化会话 (`twitter-watch`) 访问 Twitter 链接。
2. **延迟**: 随机等待 (3-7 秒) 以确保页面内容完全加载。
3. **滚动**: 执行拟人化的“向下滚动后向上滚动”操作。
4. **提取**: 精确匹配 Twitter 的指标元素（优先使用 `data-testid`，备选使用 `aria-label`）。
5. **输出**: 将单个结果保存为 `output_<slug>.json` 文件，并整合到 `twitter_report.md` 中。

## 输出文件

- `output_<tweet_id>.json`: 单条推文的详细数据。
- `twitter_report.md`: 所有已处理链接的数据汇总表。

## 环境要求

- `python3`
- 已安装并配置 `agent-browser` CLI。
