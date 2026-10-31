---
title: "06-复杂度建模与周期估算规范 (Phase 6: Complexity Modeling & Cost Estimation)"
date created: 2026-10-31 Saturday 23:22
creator: cafe3310 与 Coding Agent (Antigravity) 协作生成
background: aop-product-planner Skill 阶段六工作流规范，定义需求成本、可并行度与系统递推计算公式。
references:
  - "[[SKILL]]"
  - "[[04-ticket-design-and-dependency-graph]]"
---

# 阶段六：复杂度建模与周期估算规范 (Phase 6: Complexity Modeling & Cost Estimation)

## 1. 阶段目标与状态递推模型

本阶段建立离散状态递推与工时估算模型。

将软件开发过程视为状态演进系统。对选定的开发顺序 `S = [a -> b -> c -> d -> ...]`，系统每一步维护两个状态量：
* **`C_k`**：系统的当前复杂度。
* **`M_k`**：系统的累计维护负担。

每一个需求的实际工时，既取决于需求自身的成本，也受实施时系统状态的影响。

---

## 2. 初始状态与参数规约

### 系统初始状态
* **初始复杂度 `C_0 = 1.00`**：表示标准系统的基准阻力为 1.00。
* **初始维护负担 `M_0 = 0.00`**：表示初始无维护负担。

### 参数与参考 Anchor

以下参数除 `design_cost` 与 `deploy_cost` 为真实天数（人天）外，其余均为无量纲数：

1. **基础成本**：
   * **`design_cost` (`D_design`)**：方案设计与规划时间（人天）。
   * **`deploy_cost` (`D_deploy`)**：编码实现与测试验证时间（人天）。
2. **并行属性**：
   * **`parallelism` (`P`)**：范围 `[0.0, 1.0]`。`0.0` 表示线性阻塞（无法并行）；`1.0` 表示可以随意并行。
3. **系统交互参数**：
   * **`internal_complexity` (`I_internal`)**：参考 Anchor：修改按钮 = 0.01，增加数据库 = 0.20。
   * **`external_complexity` (`E_external`)**：参考 Anchor：对接简单系统 = 0.05，对接有状态复杂系统 = 0.20。
   * **`communication_complexity` (`K_comm`)**：参考 Anchor：视觉修改 = 0.30（增耗 30% 返工），数据导出 = 0.00。
   * **`maintenance_impact` (`M_impact`)**：参考 Anchor：引入全局拦截机制 = 0.15。

---

## 3. 递推计算公式 (Recursive Formulas)

对选定的开发顺序 `a -> b -> c -> d -> ...`，推进到第 `k` 个需求 `i` 时，使用以下公式计算工时并更新系统状态：

### 算子一：实际执行工时 f(...)

在当前系统状态 `(C_{k-1}, M_{k-1})` 下，完成需求 `i` 需要的工时 `Cost_i`（单位：人天）：

```text
Cost_i = [ D_design + D_deploy * (1 + K_comm) ] * [ C_{k-1} * (1 + E_external) + M_{k-1} ]
```

#### 计算逻辑说明：
1. **基础实际工时 `[ D_design + D_deploy * (1 + K_comm) ]`**：
   * 返工比率 `K_comm` 直接作用于编码测试天数 `D_deploy`。
   * 例：`D_deploy = 2.0` 天且 `K_comm = 0.30` 时，实际耗时为 `2.0 * 1.30 = 2.6` 天。
2. **环境放大乘数 `[ C_{k-1} * (1 + E_external) + M_{k-1} ]`**：
   * 初始状态（`C_0 = 1.00, M_0 = 0.00`）且无外部阻力（`E_external = 0.00`）时，放大系数为 `1.00`。
   * 系统演进到 `C_{k-1} = 1.30` 且需求对接复杂系统（`E_external = 0.20`）时，放大系数变为 `1.30 * 1.20 = 1.56`，总工时增加 56%。

---

### 算子二：更新系统复杂度 f2(...)

完成需求 `i` 后，系统新的复杂度为 `C_k`：

```text
C_k = C_{k-1} + I_internal
```

#### 计算逻辑说明：
* 将需求的内部复杂度 `I_internal` 累加到系统复杂度 `C` 上。
* 例：完成增加数据库的需求（`I_internal = 0.20`），系统复杂度从 `1.00` 变为 `1.20`。后续需求的计算阻力随之提高 20%。

---

### 算子三：更新维护负担 f3(...)

完成需求 `i` 后，系统新的维护负担为 `M_k`：

```text
M_k = M_{k-1} + M_impact
```

#### 计算逻辑说明：
* 将需求的长期影响 `M_impact` 累加到维护负担 `M` 上。
* 例：完成全局拦截器需求（`M_impact = 0.15`），系统维护负担从 `0.00` 变为 `0.15`，作为累加项持续作用于后续需求。

---

## 4. 序列总工时与开发顺序优化

对选定的需求序列 `S = [a -> b -> c -> d -> ...]`：

```text
序列总工时 TotalCost(S) = Cost_a + Cost_b + Cost_c + Cost_d + ...
```

### 顺序敏感性：
* 不同的开发顺序会导致系统 `C_k` 的演进路径不同，从而产生不同的 `TotalCost(S)`。
* 对比不同开发顺序的总工时，可以找到整体摩擦力最小的最佳开发顺序。

---

## 5. 阶段产出物与目录约定

本阶段产出物在项目目录中的存储位置，统一遵循：
👉 **[00-typical-directory-structure.md](00-typical-directory-structure.md)**（记录在 `D40-需求列表/` 各 Ticket 的 Frontmatter 与属性表）

---

## 6. 关联索引

* **主技能文件**：[SKILL.md](../SKILL.md)
* **网页预览**：[07-web-dashboard-and-interactive-preview.md](07-web-dashboard-and-interactive-preview.md)
