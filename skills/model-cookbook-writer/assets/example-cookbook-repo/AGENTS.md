# AGENTS: 项目章程规范 (示例)

## 1. 项目宗旨与设立背景
*   本仓库旨在以“代码化Recipes”和“可审计的Micro-benchmarks”形式，沉淀大模型的提示词调优与开发最佳实践。

## 2. 核心开发工作流：Log-loop 规范
*   **双向验证**: 每个开发的章节必须在 `benches/` 目录下有测试，且在 `bench-results/` 中有客观评测跑分数据。
*   **占位符与状态跟踪**: 
    *   `🟥` 代表未开始或待补充的占位节点。
    *   `🟩` 代表已完成节点。
    *   未完成的项目或包含未完成评测的目录在命名中加上 `_🟥_`。

## 3. 两库联动契约
*   与个人知识库双向联动。大纲源档放于 Obsidian；评测、源码和编译成果放于本仓库。

## 4. 第三方 Cookbook 引用契约 (SourceRef)
*   所有 `cookbook-chapters/**/{content,benchmarks,examples}.md` 与 `benches/*/README.md` 必须含 YAML frontmatter `sources:` 字段，声明对御三家 / 国内厂商 cookbook 的引用关系。
*   单条 source 至少包含：`vendor / repo / path / upstream_url / snapshot_commit / relation`；relation ∈ {borrows-from, benchmarks-against, counter-example, extends}。
*   原创推导写 `sources: []` 并在 note 注明。详见 model-cookbook-writer SKILL.md §4。

## 5. 目录结构
```
├── AGENTS.md                  # 本章程
├── TODO.md                    # 任务日志
├── cookbook-chapters/         # 章节分类树
├── benches/                   # 微评测用例 (平铺)
├── bench-results/             # 跑分结果归档 (平铺)
└── cookbooks/                 # 交付项目 (平铺)
```
