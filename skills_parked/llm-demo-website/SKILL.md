---
name: llm-demo-website
description: 基于联网审美深度搜索与设计提示词，一键生成极具视觉表现力的单页面设计风格与组件演示站
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
---

# LLM Demo Website (Design & Concept Showcase Generator)

当个设计大师和前端专家。根据用户提示，完整、相近地写出用户所需的视觉风格的特点，包括颜色，样式，布局，给人的感受，体现的情感，对比，文字排版风格等。将这些内容标准化成 tailwindcss 和普通 css 表达的样式，以及 html 表达的组件。结合互联网最新的前沿审美，生成极具视觉表现力、适合演示与展示的单页面 HTML 设计系统演练场（Showcase）。

---

## 技术栈规范

1. 样式方案：
使用 Tailwind CSS CDN 快速搭建页面的网格与骨架结构：
  ```html
  <script src="https://cdn.tailwindcss.com"></script>
  ```
 - 配合内联 `<style>` 块，使用 Vanilla CSS 与现代配色颜色函数定义精细的微动效、投影、特殊渐变及高端视觉微调。

 2. 图标库：
使用 Lucide 原生 JS 版图标库。
  - 在 head 引入：<script src="https://unpkg.com/lucide@latest"></script>
  - 在 body 中使用属性占位，例如：<i data-lucide="camera" color="red"></i>
  - 必须在 body 最底部或 DOM 加载后执行：<script>lucide.createIcons();</script>


3. 占位图（LoremFlickr）：
使用 LoremFlickr 接口获取符合网页视觉风格和主题的真实占位图：
   - 格式：`https://loremflickr.com/{宽度}/{高度}/{关键词}`
   - 示例：`https://loremflickr.com/800/600/abstract,minimalist`

---

## 执行工作流

当用户要求设计某种视觉风格或主题的演示站时，Agent 必须严格执行以下步骤：

### 1. 深度审美搜索

要求：不能仅凭大模型自身的静态知识，必须执行尽可能丰富的、不同维度的深度搜索：

  1. 检索垂直风格在业界的最前沿体现（如 `"modern minimal layout Awwwards"`）。
  2. 检索具体的高级配色方案与配色色值范例（如 `"linear app design system colors 配色"`）。
  3. 检索特定动效与交互技巧（如 `"smooth hover card border css micro-interactions"`）。

分析沉淀：以 Markdown 形式向用户完整阐述该风格的视觉特点，包括：

- 核心感受与情感：该设计带给用户的物理场景联想与情绪张力。
- 色彩与对比：主色调、辅助色及前景与背景的配色对比逻辑。
- 网格与布局：页面的视觉动线、不对称布局或变形。
- 文字排版：选用的 Google Fonts 字体配对、字重对比与行高字距。

### 2. 区块划分与设计

详细定义各个区块的视觉表现、内容文案与拟呈现的交互。你可以自由添加合适的内容，包括：

- Hero 部分：用尽可能直观的方式展示该风格的调性，be impressive。
- 配色和主题色版
- 组件列表，装饰，阴影等风格
- 文字和排版风格
- 更多关于此视觉设计风格的描述。

### 3. 样式与组件标准化（Design System Definition）

将第 1、2 步确立的设计提案转化为代码级的标准化规范：

- Tailwind 配置拓展：写出自定义颜色、字体、阴影的类名映射。
- CSS 自定义属性：使用配色定义一组核心配色变量（如 `--bg`, `--fg`, `--primary`, `--accent`）。
- 核心组件定义：规定核心卡片、按钮、分割线的 CSS 表达。

### 4. 生成高完成度单页面 HTML

整合上述内容，编写完整的单页面 HTML，力求完美呈现。
