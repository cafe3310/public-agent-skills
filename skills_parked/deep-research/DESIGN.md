# 设计：深度研究可视化器 (Deep Research Visualizer)

## 核心 Token (OKLCH)

### 颜色策略：Committed
一款突出聚焦强调色的技术暗色主题。

- **背景 (Background)**：`oklch(18% 0.01 260)`
- **表面 (Surface)**：`oklch(22% 0.01 260)`
- **表面提升 (Surface Elevated)**：`oklch(26% 0.02 260)`
- **边框 (Border)**：`oklch(30% 0.02 260)`
- **主要文本 (Text Main)**：`oklch(88% 0.01 260)`
- **静音文本 (Text Muted)**：`oklch(60% 0.01 260)`
- **强调色 (Accent)**：`oklch(65% 0.15 255)`（精确蓝）
- **成功状态 (Success)**：`oklch(70% 0.12 150)`（暗薄荷绿）
- **警告状态 (Warning)**：`oklch(60% 0.15 30)`（工业橙）

## UI 基元 (UI Primitives)

- **边框 (Borders)**：严格为 1px。结构线不要使用 0px 或 2px 及以上。
- **圆角 (Corners)**：`radius: 2px`（硬边缘）。
- **字体 (Typography)**：
  - 无衬线 (Sans)：Inter, 系统无衬线字体 (UI 标签)
  - 等宽 (Mono)：JetBrains Mono, Fira Code, 系统等宽字体 (技术数据、片段)
- **间距 (Spacing)**：
  - 网格：基准 4px。
  - 标准间隙 (Standard Gap)：12px。
  - 版块内边距 (Section Padding)：20px。

## 布局原则 (Layout Principles)
- **单体面板 (Monolithic Panels)**：使用具有内部滚动的全高面板。
- **锋利分隔 (Sharp Separation)**：通过 1px 边框或微妙的背景色过渡来区分区域，不要使用阴影。
- **操作 UI (Action UI)**：按钮扁平、锋利，悬停时具有高对比度。
