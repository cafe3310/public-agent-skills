#!/bin/bash
# init_example_kb.sh
# 此脚本用于初始化一个示例的 memories-off 知识库，展示 learning-assistant 的核心实体。

# 设置示例知识库的目录
export MEMORIES_OFF_DIR="./example_kb"
mkdir -p "$MEMORIES_OFF_DIR"

echo "开始初始化示例知识库到目录: $MEMORIES_OFF_DIR"

# 1. 全局状态
memocli create-entity --name "当前学习状态" --type "状态"
memocli append-update --name "当前学习状态" --observations "当前主题：Rust编程, 当前计划：Rust编程-基础语法"

# 2. 学习主题
memocli create-entity --name "Rust编程" --type "学习主题"

# 3. 学习计划
memocli create-entity --name "Rust编程-基础语法" --type "学习计划" --add-rel-out "BELONGS_TO:Rust编程"
# 使用假装的 update-chapter 命令的形式，这里用 append-update 模拟内容写入
memocli append-update --name "Rust编程-基础语法" --observations "## 已学习内容
- Rust编程-基础语法-变量绑定

## 待学习内容
- Rust编程-基础语法-数据类型
- Rust编程-基础语法-所有权"

# 4. 资料
memocli create-entity --name "Rust编程-基础语法-官方文档" --type "资料" --add-rel-out "BELONGS_TO:Rust编程-基础语法"

# 5. 概念
# 已学习的概念
memocli create-entity --name "Rust编程-基础语法-变量绑定" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法"
memocli append-update --name "Rust编程-基础语法-变量绑定" --observations "状态：已掌握。反馈：理解了 let 和 mut 的区别。"

# 待学习的概念
memocli create-entity --name "Rust编程-基础语法-数据类型" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法"
memocli append-update --name "Rust编程-基础语法-数据类型" --observations "状态：未开始"

memocli create-entity --name "Rust编程-基础语法-所有权" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法"
memocli append-update --name "Rust编程-基础语法-所有权" --observations "状态：未开始"

# 6. 学习日志
TODAY=$(date +%Y%m%d)
memocli create-entity --name "学习日志-$TODAY" --type "学习日志" --observations "创建了 Rust编程 主题，并开始 基础语法 计划。完成了变量绑定的学习。"

echo "示例知识库初始化完成！"
echo "你可以通过执行: memocli info --name '当前学习状态' (确保设置了 MEMORIES_OFF_DIR) 来检查。"
