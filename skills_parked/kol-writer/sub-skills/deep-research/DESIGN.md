# Design: Deep Research Visualizer

## Core Tokens (OKLCH)

### Color Strategy: Committed
A technical dark theme with a focused accent role.

- **Background**: `oklch(18% 0.01 260)`
- **Surface**: `oklch(22% 0.01 260)`
- **Surface Elevated**: `oklch(26% 0.02 260)`
- **Border**: `oklch(30% 0.02 260)`
- **Text Main**: `oklch(88% 0.01 260)`
- **Text Muted**: `oklch(60% 0.01 260)`
- **Accent**: `oklch(65% 0.15 255)` (Precise Blue)
- **Success**: `oklch(70% 0.12 150)` (Muted Mint)
- **Warning**: `oklch(60% 0.15 30)` (Industrial Orange)

## UI Primitives

- **Borders**: Strictly 1px. No 0px or 2px+ for structural lines.
- **Corners**: `radius: 2px` (Hard-edged).
- **Typography**: 
  - Sans: Inter, System Sans (UI labels)
  - Mono: JetBrains Mono, Fira Code, System Mono (Technical data, snippets)
- **Spacing**: 
  - Grid: 4px base.
  - Standard Gap: 12px.
  - Section Padding: 20px.

## Layout Principles
- **Monolithic Panels**: Use full-height panels with internal scrolling.
- **Sharp Separation**: Distinguish areas via 1px borders or subtle background shifts, not shadows.
- **Action UI**: Buttons are flat, sharp, and high-contrast on hover.
