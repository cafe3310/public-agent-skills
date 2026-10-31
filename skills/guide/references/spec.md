# Subcommand: `/guide spec` (长期生效规范管理与应用)

## 1. 核心定位与双重模式

`/guide spec` 是系统长期架构契约（Specifications）的管理与执行指令，具备**积累长效规范**与**重新加载/纠偏应用规范**双重能力：

- **模式 A：积累 / 记录 Spec (Accumulate Spec)** —— 当用户提出长期生效的架构准则、数据契约或开发禁忌时，按合理抽象层级沉淀到规范库中；
- **模式 B：应用 / 纠偏 Spec (Apply & Re-align Spec)** —— 当用户发现 Agent 忘掉、偏离或违反既定规范时，强力重新加载关联 Spec 并对照审查代码、即刻纠偏。

---

## 2. 模式 A：积累 Spec 的执行准则与流程

### 2.1 触发与确认原则 (Pre-Record Confirmation)
- **记录前必须向用户询问确认**：无论是由 `/guide spec` 显式触发，还是在执行 `/guide log` 等收尾任务时识别到了潜在长效规约，**在真正写入或修改 `specifications/` 文件之前，Agent 必须先将提炼出的 Spec 标题与核心抽象要点向用户明确询问，获得用户确认后再行落盘**；
- Agent **严禁在未经用户确认的情况下擅自将临时结论写入 Spec**。

### 2.2 合理抽象程度准则 (Reasonable Abstraction Principle)
- Spec 应该保持整体和合理的抽象高度，具备全局指导性，而非针对当前局部狭隘现状的代码级修补；
- 提炼规范时，应当关注通用的架构原则、数据契约、分层边界或开发范式，避免直接绑定到临时或具体的单个类、函数或局部实现细节上。

### 2.3 规范存放位置与文件组织
- 统一存放在 `{文档目录}/specifications/` 目录下（如 `docs/specifications/`）；
- 采用语义化或序号前缀命名（如 `01-module-boundaries.md`、`02-type-system.md`）；
- 每次新增 Spec，同步更新 `{文档目录}/specifications/README.md` 索引清单。

---

## 3. 模式 B：应用与纠偏 Spec 的执行流程

当用户输入 `/guide spec` 或指出 Agent 偏离规范时：

1. **定向重新深读**：立即打开并完整阅读 `{文档目录}/specifications/` 中涉及的 Spec 正文；
2. **合规性审查 (Compliance Audit)**：
   - 逐条对照 Spec 中的「强制准则」与「禁止的反模式（Prohibitions）」；
   - 排查当前代码、目录结构或设计方案中的违规点；
3. **输出纠偏方案**：向用户明确指出偏离项，并给出符合 Spec 规范的手术式修正代码。

---

## 4. Spec 标准文档模板

创建或更新规范时，必须遵循以下标准结构与 Frontmatter 元数据：

```markdown
+++
title = "{简明规范标题}"
date_created = "YYYY-MM-DD HH:mm"
creator = "cafe3310 与 Coding Agent 协作生成"
background = "简述沉淀该规范的架构背景、核心驱动力与长效价值"
references = ["file:///path/to/related/spec.md"]
+++

# {简明规范标题}

## 1. 概述与核心哲学 (Core Philosophy)
- 阐明该规范在整个系统架构中的核心定位与指导思想。

## 2. 分层模型与数据契约 (Architecture & Contracts)
- 详细说明分层职责、名义类型定义、接口结构或数据模型。

## 3. 强制准则与实施流程 (Mandatory Rules)
- 必须严格遵循的工程实践（包含正向示例代码）。

## 4. 严禁触碰的反模式禁忌 (Prohibitions & Anti-patterns)
- 以 ❌ 明确列出绝对禁止的做法、危害及对应的 ✅ 正确做法。
```
