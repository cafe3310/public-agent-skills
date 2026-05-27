---
name: online-content-collector
description: 全库自动化素材剪藏。扫描 `#marker-待下载` 标签，生成下载列表，并本地化网页、视频及附件至 Obsidian 仓库。
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - yt-dlp
  - pandoc
  - ffmpeg
  - python3
---

# 技能：线上素材收集器 (Online Content Collector)

## 概述

此技能旨在实现从“发现链接”到“本地化存档”的完全自动化。它扫描 Obsidian 仓库中带有特定标签的链接，将其汇总并下载为包含文本、图片、视频及附件的完整本地 Markdown 存档。

## 核心配置解析

此技能依赖用户 Vault 根目录下的 `AGENTS.md`。**Agent 在执行脚本前，必须首先读取此文件**，并解析出以下路径：
- `下载列表目录位于`: 用于传递给 `--list-dir`。
- `下载内容目录位于`: 用于传递给 `--archive-dir`。

---

## 核心工作流

### 第一阶段：扫描与汇总 (Discovery & Aggregation)
1. **配置读取**: Agent 读取 `AGENTS.md`，确定目标路径。
2. **执行脚本**: 调用 `scripts/collect_links.py`，传入 `--vault-path` 和 `--list-dir`。
3. **元数据提取与更新**: 脚本扫描包含 `#Marker-待下载` 的文件，提取 `time` 和 `source`，生成 YAML 格式的任务列表 `[yyyy-mm-dd-hh 下载列表整理.md]`，并将原始文件标签更新为 `#Marker-下载中-YYYYMMDD`。

### 第二阶段：用户确认 (User Confirmation)
1. **停止并检查**: Agent 输出 YAML 列表文件路径，等待用户确认。

### 第三阶段：执行下载与剪藏 (Execution & Archival)
1. **执行脚本**: 调用 `scripts/process_downloads.py`，传入 `--list-file` 和 `--archive-dir`。
2. **任务处理与分发**:
    - **YouTube / X (Twitter)**: 使用 `yt-dlp` 下载。请求最高画质，必须下载并保留全量 JSON 元数据（`--write-info-json`）。
    - **未知站点**: 如果无法识别域名或未配置下载方式，则直接标记为“下载失败（未识别站点）”，不进行尝试。
3. **隔离目录创建**: 为每个下载任务创建独立目录，命名规范：`[YYYY-MM-DD-HH] {分类} {描述/ID}`。
4. **内容本地化**:
    - **主文档**: 在目录下创建一个同名的 `.md` 文件。
    - **资产存放**: 所有的 `.mp4`, `.json`, `.jpg` 等资产**全部存放在该任务目录下**。
    - **引用关联**: Markdown 文件中使用本地相对路径链接同目录下的视频。

### 第四阶段：状态汇报与闭环 (Reporting & Closing)
1. **列表回写**: 脚本在 YAML 列表中更新状态为“下载完成”或“下载失败”。
2. **标签同步**: Agent 根据脚本输出，将原始文件中的链接标签更新为 `#Marker-已下载-YYYYMMDD`。

---

## 依赖工具

- **yt-dlp**: 视频抓取。
- **MarkItDown / Pandoc**: 网页转 Markdown。
- **ffmpeg**: 视频合并。

## 最佳实践

- **路径对齐**: 始终从 `agents.md` 读取路径，不要硬编码。
- **元数据保留**: 在剪藏的 Markdown 头部记录原始 URL 和收集时间。
- **异常容错**: 下载失败时记录错误原因，不中断后续任务。
