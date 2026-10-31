---
title: "07-可交互网页预览与需求勾选计算器规范 (Phase 7: Web Dashboard & Interactive Preview)"
date created: 2026-10-31 Saturday 23:24
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 阶段七工作流规范，定义自动生成单文件 HTML/JS 预览面板与需求勾选计算器的流程。
references:
  - "[[SKILL]]"
  - "[[06-complexity-modeling-and-cost-estimation]]"
---

# 阶段七：全景需求架构 Finder 网页与双色 Hover 高亮编译规范 (Phase 7: Web Dashboard & Finder Mesh Preview)

## 1. 阶段目标与网页预览架构

本阶段将项目中的 Markdown 策划文档（`D10` 叙事、`D20` 目标、`D30` 切面大网、`D40` 需求 Tickets 及中文 SVG 示意图）自动合并编译为一个离线可用的单文件 HTML 架构全景面板。

该面板借鉴了 **macOS Finder 多级列视图 (Column Layout)** 界面哲学，结合神经网络式单级 Hover 双色高亮、全文 Modal 弹窗及关联节点【优先置顶】重排对比机制。

---

## 2. 网页架构与交互规约 (UX Specification)

### 2.1 macOS Finder 4 列竖向分栏布局
界面横向并排 4 个独立的竖向滚动列面板：
* **Column 1 (左一列)**：📖 `D10 故事与定位叙事`（纵向列表与滚动）；
* **Column 2 (左二列)**：🎯 `D20 平台目标与重点`（显示关联 `D1x` 标签）；
* **Column 3 (左三列)**：🧩 `D30 AOP 切面大网`（显示关联 `D2x` 标签）；
* **Column 4 (左四列)**：📋 `D40 需求 Tickets`（显示关联 `D3x` 标签及 SVG 示意图）。

### 2.2 跨列单级 (1-Hop) Hover 双色高亮法则
* **指向节点 (Hover Target)**：亮蓝色大阴影发光 (`border-color: #0088ff; box-shadow: 0 0 24px rgba(0, 136, 255, 0.7);`) + 3% 放大微浮；
* **直接相邻 1 级节点 (Direct 1-Hop Neighbor)**：天蓝色发光 (`border-color: #38bdf8; box-shadow: 0 0 16px rgba(56, 189, 248, 0.5);`)；
* **越级与无关节点**：`opacity: 0.18; filter: grayscale(85%)` 淡化；
* **严禁越级高亮**：指向 `D3x` 时仅高亮 `D3x` 自身与相邻一级的 `D2x` 和 `D4x`，`D1x` 保持淡化。

### 2.3 `[ 📖 详情 ]` Modal 全文查看
卡片 Hover 时右上角浮现 `[ 📖 详情 ]` 按钮，点击唤起暗色毛玻璃 Backdrop 弹窗，展现全量文档 Markdown 内容及内嵌的中文看图讲故事 SVG 示意图。

### 2.4 `[ 📌 优先 ]` 节点置顶对比与 Hover 拦截
* **一键置顶重排**：点击 `[ 📌 优先 ]` 按钮，系统自动将当前节点及其所有相邻 1 级节点 `prepend` 移动置顶至各自列最顶端，方便一屏并排对比；
* **优先模式下禁止 Hover**：当处于【优先置顶】模式时，**全面禁止鼠标悬停感应的高亮切换**，避免打扰用户注意力；点击顶栏“取消优先置顶 ✕”后解除禁止并复位。

---

## 3. 标准编译流程与 CLI 工具 (CLI & Build SOP)

使用技能自带的可执行 CLI 工具进行 4 层数据提取、完整性审计及网页编译：

```bash
# 1. 提取全量四层元数据与拓扑，进行遗漏/断链审计，导出 YAML 或 TOML 格式
python3 scripts/extract_and_audit_mesh.py \
  --root-dir "/path/to/project" \
  --layer1-dir "/path/to/D10-narrative" \
  --layer2-dir "/path/to/D20-targets" \
  --layer3-dir "/path/to/D30-aspects" \
  --layer4-dir "/path/to/D40-tickets" \
  --format yaml \
  --output "/path/to/project/preview/mesh_audit.yaml"

# 2. 运行全量网页编译脚本，将节点、SVG 图表及审计结果整合为离线 HTML Dashboard
python3 scripts/compile_mesh_dashboard.py \
  --root-dir "/path/to/project" \
  --layer1-dir "/path/to/D10-narrative" \
  --layer2-dir "/path/to/D20-targets" \
  --layer3-dir "/path/to/D30-aspects" \
  --layer4-dir "/path/to/D40-tickets" \
  --output "/path/to/project/preview/index.html"

# 3. 在 macOS 默认浏览器中打开预览
open "/path/to/project/preview/index.html"
```

---

## 4. 阶段产出物与目录约定

本阶段产出物在项目目录中的存储位置，统一遵循：
👉 **[00-typical-directory-structure.md](00-typical-directory-structure.md)**（主要存储在 `/tmp/project_requirements_preview.html` 或 `preview/index.html`）

---

## 5. 关联索引

* **主技能文件**：[SKILL.md](../SKILL.md)
* **复杂度建模**：[06-complexity-modeling-and-cost-estimation.md](06-complexity-modeling-and-cost-estimation.md)
