---
name: openslide
description: >
  Mandatory entry point for creating, editing, and maintaining slide decks with the open-slide framework.
  Acts as the composite skill router containing 5 specialized subskills in subskills/<name>:
  slide-authoring (1920x1080 canvas, typography, layout, budget math, transitions, morph, speaker notes),
  create-slide (deck creation workflow, scoping questionnaire, structure planning),
  apply-comments (processing in-browser inspector @slide-comment markers),
  current-slide (resolving deictic references to current slide/element via current.json),
  create-theme (authoring reusable theme bundles under themes/).
  Directs agents to read subskills/<name>/SKILL.md on demand without cluttering the global skill namespace.
license: MIT
author: https://github.com/1weiho/open-slide
depends_on_skill: []
depends_on_binary:
  - node
  - npx
  - pnpm
---

# open-slide 幻灯片开发套件 (Master Composite Skill)

本技能是使用 `open-slide` 框架制作、编辑和维护 React 驱动幻灯片演示（Slide Deck）的总控入口与复合技能路由器（Composite Skill Router）。

> **复合技能架构说明 (Composite Skill)**：  
> 本技能为一级入口。框架所包含的 5 个专项子技能及详细技术规范均收纳在当前目录下的 **`subskills/<name>/`**。  
> 当确定具体执行任务时，**请读取对应的 `subskills/<name>/SKILL.md` 文档**（当子技能内部提及查阅 `slide-authoring`、`current-slide` 等兄弟技能时，均对应 `subskills/<name>/SKILL.md`）。

---

## 1. 任务意图路由表 (Intent Routing Table)

根据当前交互目标与用户意图，匹配对应的子技能文档读取并执行：

| 任务场景 / 用户意图 | 目标动作 | 需加载的子技能 | 相对路径 |
| :--- | :--- | :--- | :--- |
| **新建 Slide Deck** / "制作一套幻灯片" / "起草 PPT" | 锁定主题、向用户澄清 4 项风格决策（美学方向、页数、文本密度、动效）、规划结构并初始化 `slides/<id>/index.tsx` | `create-slide` | `subskills/create-slide/SKILL.md` |
| **编写/修改具体页面** / 调整布局、排版、配色、动效、讲者讲稿 | 查阅 1920×1080 画布约束、垂直预算计算、Design Tokens、转场动效、形变连续性与 `notes` 讲稿规范 | `slide-authoring` | `subskills/slide-authoring/SKILL.md` |
| **指代词定位** / 用户说 "改下这页"、"当前页"、"把这个标题调大" | 读取 `node_modules/.open-slide/current.json` 实时游标，解析用户在 Dev Server 正在查看的 slideId、pageIndex 及选中的 JSX 元素 | `current-slide` | `subskills/current-slide/SKILL.md` |
| **处理批注反馈** / "应用 Inspector 评论" / 源码中存在 `@slide-comment` | 扫描 `slides/<id>/index.tsx` 中的批注标记，逆序精准修改 JSX 并清理标记 | `apply-comments` | `subskills/apply-comments/SKILL.md` |
| **创建全局主题** / 提取设计规范为可复用 Theme | 生成 `themes/<id>.md`（规范）与 `themes/<id>.demo.tsx`（Live Preview）双文件主题包 | `create-theme` | `subskills/create-theme/SKILL.md` |

---

## 2. 专项子技能概览 (Subskills Overview)

### 2.1 `create-slide` — 幻灯片新建流程 (`subskills/create-slide/SKILL.md`)
- **核心职能**：引导完成 Deck 的从 0 到 1 策划。
- **关键阶段**：
  1. 检查 `themes/` 是否有可用主题并引导选择；
  2. 澄清 4 大核心要素（美学方向、预期页数、文本密度、动效偏好）；
  3. 确定 kebab-case 格式的 `slideId`；
  4. 规划页面角色（Cover, Agenda, Section, Content, Big number, Quote, Comparison, Closing）；
  5. 委托 `slide-authoring` 写入 `slides/<id>/index.tsx`。

### 2.2 `slide-authoring` — 页面编码与技术基准 (`subskills/slide-authoring/SKILL.md`)
- **核心职能**：所有页面 React 代码实现的底层契约与技术规范。
- **关键技术点**：
  - 画布尺寸固定 **1920 × 1080**，绝对 `px` 数值，严禁 `rem`/`vw`/`vh`。
  - **严防垂直溢出**：画布不可滚动，内容高度必须严格预算（$\text{Usable} = 1080 - 2 \times \text{padding}$）。超预算必须拆页，严禁压缩字号或减小 padding 硬塞。
  - **禁止 `array.map`**：重复卡片/列表项必须在 JSX 中显式单独实例化，确保 In-browser Inspector 能够精准选定和编辑单个节点。
  - **模块契约**：单套 Deck 默认是单一入口 `slides/<id>/index.tsx` + `assets/`（除非项目 `AGENTS.md` 另有分文件约定）。
  - **讲者讲稿**：必须通过 `export const notes: (string | undefined)[]` 导出并与页面索引对齐，供 Presenter 模式读取。严禁以单独的 markdown 文件交付讲稿。
  - **视觉预览**：Dev Server 启动时，可通过 `/s/<id>/preview?p=N` 路由进行无头截图或渲染审查。
  - **底层原语规范索引**：见 `subskills/slide-authoring/references/`：
    - `design-system.md`（`export const design: DesignSystem` 与 `var(--osd-X)` 变量）
    - `assets.md`（静态资源导入与 `<ImagePlaceholder>`）
    - `webfonts.md`（自定义字体与 CJK 子集化加载）
    - `page-numbers.md`（`useSlidePageNumber()` 页码 Hook）
    - `steps.md`（`<Steps>` / `<Step>` 分步揭示）
    - `transitions.md`（`SlideTransition` 页面切换动效）
    - `morph.md`（`MorphElement` 跨页连续形变 Magic Move）

### 2.3 `current-slide` — 实时游标解析 (`subskills/current-slide/SKILL.md`)
- **核心职能**：当用户使用代词（"这页"、"当前页"、"选中的卡片"）时，通过读取 `node_modules/.open-slide/current.json` 确定具体的 Slide、Page 及精确的 AST 元素位置，避免向用户反复追问。
- **时效性要求**：每次用户交互均需重新读取，禁止跨轮次缓存。

### 2.4 `apply-comments` — Inspector 批注处理 (`subskills/apply-comments/SKILL.md`)
- **核心职能**：处理用户在浏览器 Inspector 模式下直接打在页面上的文字批注（`@slide-comment` 格式）。
- **处理原则**：Base64url 解码批注意图，按源码行号由下至上逆序手术式修改 JSX，修改后彻底清除标记，并核验证实无语法错误。

### 2.5 `create-theme` — 主题包制作 (`subskills/create-theme/SKILL.md`)
- **核心职能**：制作可复用的视觉主题，输出成对的 `themes/<id>.md`（文档与组件规范）与 `themes/<id>.demo.tsx`（Themes 面板实时预览）。

---

## 3. 核心开发禁忌速查 (Hard Rules)

1. **严禁使用 `array.map` 渲染重复 UI 元素**（必须在 JSX 中独立实例化各组件）。
2. **严禁溢出 1080px 垂直高度**，严禁使用 `overflow: auto/scroll/hidden` 隐藏溢出。
3. **严禁使用相对视口单位**（`rem`、`vw`、`vh`），正文字体不低于 28px。
4. **严禁修改 `package.json`、`open-slide.config.ts` 或其他无关 Slide**，不安装额外依赖。
5. **严禁以独立的 `.md` 交付讲稿**，必须写入 `export const notes` 数组。
