---
name: hugging-face-stat
description: 专门用于获取 Hugging Face 上的模型、数据集和 Space 的详细统计信息，包括历史总下载量。
author: github/cafe3310
license: Apache-2.0
---

# Skill: hugging-face-stat

## 1. 概述 (Overview)

Hugging Face 官方页面默认主要展示“过去 30 天的下载量”。此技能通过底层的 API 扩展参数，允许大语言模型获取任意公开模型或数据集的**历史总下载量 (downloadsAllTime)**，以及获取 Space 的运行硬件、点赞数与状态，并能汇总查询组织下所有模型的数据。

此技能提供了一个可靠的 Bash 脚本（`hf_stats.sh`），自带错误处理、超时机制和数值美化。

## 2. 核心功能与使用方法 (Core Capabilities & Usage)

本技能提供了一个现成的 Bash 脚本 `hf_stats.sh`。当你需要查询 Hugging Face 数据时，**必须**直接调用该脚本。

### 脚本路径
`/Users/sipan/workspace/public-agent-skills/skills/hugging-face-stat/hf_stats.sh`

### 场景 A: 查询模型或数据集 (Model / Dataset)
当你需要查询一个模型或数据集的详细下载数据时：
```bash
# 查询模型
/Users/sipan/workspace/public-agent-skills/skills/hugging-face-stat/hf_stats.sh model <repo_id>
# 查询数据集
/Users/sipan/workspace/public-agent-skills/skills/hugging-face-stat/hf_stats.sh dataset <repo_id>
```
返回数据包括：库 ID、作者、创建时间、最近30天下载、历史总下载量、点赞数。

### 场景 B: 查询空间 (Space)
当你需要了解一个 Space 的热度与运行环境时：
```bash
/Users/sipan/workspace/public-agent-skills/skills/hugging-face-stat/hf_stats.sh space <repo_id>
```
返回数据包括：库 ID、运行状态、硬件规格（如 T4 medium）、SDK 类型（如 Gradio）、点赞数。

### 场景 C: 查询组织 (Organization)
当你需要汇总查询一个组织下所有模型的统计数据时：
```bash
/Users/sipan/workspace/public-agent-skills/skills/hugging-face-stat/hf_stats.sh org <org_name>
```
返回数据包括：组织模型总数、最近30天总下载、总点赞数，并按下载量降序排列前20个热门模型。

## 3. 工作流 (Workflow)

1. **意图识别**: 当用户询问“某个模型的总下载量”、“这个模型是什么时候创建的”、“这个 Space 跑在什么硬件上”或“这个组织一共有多少个模型”时，触发此技能。
2. **提取参数**: 提取目标库的 `repo_id` 和类型（`model`, `dataset`, `space`, `org`）。
3. **执行工具**: 使用 `Bash` 工具运行本技能目录下的 `hf_stats.sh` 脚本。
4. **解析与回复**:
   - 将脚本返回的格式化结果整理成自然语言。
   - 强调**历史总下载量**，这是用户最关注且网页端较难直接获取的数据。
   - 提及 Space 的**硬件规格**和 **SDK**，帮助用户评估其运行性能。
   - 如果是查询 Space 的访问量，必须向用户澄清：“Hugging Face 官方未公开 Space 的实时访问量数据，目前通过点赞数和硬件规格来评估其热度和资源投入”。

## 4. 限制说明
- Hugging Face API 仅提供“过去30天”和“历史总和”两个快照。无法直接回溯任意日期的历史趋势折线图。
- 组织查询受 API 汇总限制，无法直接获取组织级的“历史总下载量”累加值，仅显示最近30天累加值。
- 如果查询遇到 404，提醒用户检查 ID 是否正确或仓库是否为私有。
