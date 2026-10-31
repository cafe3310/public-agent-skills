---
name: online-content-collector
description: 对 Obsidian 仓库进行自动素材媒体剪藏，本地化特定 tag 标注的网页、视频及附件
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

### 第五阶段：看版预览与可视化 (Visualization & Viewer - 可选)
1. **看版部署**: 当用户请求以网页形式可视化这些收藏信息时，Agent 从该技能的 `templates/viewer/` 中拷贝 `index.html`、`style.css`、`app.js`、`server.js` 以及 `compile_single_page.py` 五个文件至“下载内容目录”下。若有需要，也可将 `scripts/generate_data.py` 拷入。
2. **启动 Node 服务**: 引导用户在该目录下运行 `node server.js`，启动 8000 端口的极简工业风本地服务器。
3. **自动生成视频缩略图**: 启动服务时，Node 程序会自动分析该目录下所有纯视频的子目录，使用本机的 `ffprobe` 获取时长、使用 `ffmpeg` 精准截取 1/3 进度处的帧（限定最大宽度 640px 并进行 -strict 兼容转码），生成极轻量级的 `thumbnail.jpg` 充当网页卡片的封面图，在右上角带上“视频”标识。
4. **一键刷新同步**: 当有新的网络收藏被下载完毕后，用户无需重启服务，只需在浏览器中刷新网页，后台便会自动重新执行扫描以实现无感动态数据更新。
5. **一键打包单页面 (Portable Single-Page HTML)**: 若用户需要导出一个完全独立的单 HTML 文件（无需外部相对路径依赖，可离线查看），可引导用户在下载内容目录下运行 `python3 compile_single_page.py`。该脚本会对所有图片进行缩减压缩（长边最大 400px 且默认限制 45% WebP 质量），转换为 Base64 嵌入至单个页面内，同时对视频文件路径进行隔离（在单页面模式下视频点击直接引导至介绍页下载），生成仅数兆大小的 `index_single.html`，极利于分发便携分享。

---

## 依赖工具

- **yt-dlp**: 视频抓取。
- **MarkItDown / Pandoc**: 网页转 Markdown。
- **ffmpeg & ffprobe**: 视频合并、缩略图提取与时长分析。
- **Node.js**: 用于本地看版静态服务器运行（免装依赖）及自动磁盘扫描。

## 最佳实践

- **路径对齐**: 始终从 `agents.md` 读取路径，不要硬编码。
- **元数据保留**: 在剪藏的 Markdown 头部记录原始 URL 和收集时间。
- **异常容错**: 下载失败时记录错误原因，不中断后续任务。
- **看版引导**: 每次在下载剪藏任务全部处理完毕后，**主动向用户提示**：可以使用我们配套的本地直角工业风看版进行大屏极简可视化探索，运行 `node server.js` 即可启动。
