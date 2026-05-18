#!/bin/bash
export MEMORIES_OFF_DIR="skills/learning-assistant/example_kb"

# Clean up existing dir if any
rm -rf "$MEMORIES_OFF_DIR"
mkdir -p "$MEMORIES_OFF_DIR"

echo "Building Knowledge Base..."
R="--reason 初始化示例数据"

# 1. 全局状态
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "当前学习状态" --type "状态"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "当前学习状态" -c "当前主题：Rust编程, 当前计划：Rust编程-所有权机制"

# 2. 主题一：Rust编程
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程" --type "学习主题"

# 计划 1.1 (已完成)
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-基础语法" --type "学习计划" --add-rel-out "BELONGS_TO:Rust编程"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-基础语法" -c "## 已学习内容
- Rust编程-基础语法-变量绑定
- Rust编程-基础语法-数据类型

## 待学习内容
无
"

memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-基础语法-变量绑定" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-基础语法-变量绑定" -c "状态：已掌握"
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-基础语法-数据类型" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-基础语法"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-基础语法-数据类型" -c "状态：已掌握"

# 计划 1.2 (进行中)
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-所有权机制" --type "学习计划" --add-rel-out "BELONGS_TO:Rust编程"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-所有权机制" -c "## 已学习内容
- Rust编程-所有权机制-借用与引用

## 待学习内容
- Rust编程-所有权机制-生命周期
"

memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-所有权机制-借用与引用" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-所有权机制"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-所有权机制-借用与引用" -c "状态：已掌握。要点：同一作用域内，不可变引用可有多个，可变引用只能有一个。"

memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "Rust编程-所有权机制-生命周期" --type "概念" --add-rel-out "BELONGS_TO:Rust编程-所有权机制"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "Rust编程-所有权机制-生命周期" -c "状态：未开始"

# 3. 主题二：微服务架构
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "微服务架构" --type "学习主题"

# 计划 2.1 (未开始)
memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "微服务架构-Docker基础" --type "学习计划" --add-rel-out "BELONGS_TO:微服务架构"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "微服务架构-Docker基础" -c "## 已学习内容
无

## 待学习内容
- 微服务架构-Docker基础-镜像与容器
- 微服务架构-Docker基础-Dockerfile编写
"

memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "微服务架构-Docker基础-镜像与容器" --type "概念" --add-rel-out "BELONGS_TO:微服务架构-Docker基础"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "微服务架构-Docker基础-镜像与容器" -c "状态：未开始"

memocli create-entity -p "$MEMORIES_OFF_DIR" $R --name "微服务架构-Docker基础-Dockerfile编写" --type "概念" --add-rel-out "BELONGS_TO:微服务架构-Docker基础"
memocli append-update -p "$MEMORIES_OFF_DIR" $R -e "微服务架构-Docker基础-Dockerfile编写" -c "状态：未开始"

# 4. 移除 .git 目录
echo "Removing .git directory..."
rm -rf "$MEMORIES_OFF_DIR/.git"

echo "Example KB created successfully at $MEMORIES_OFF_DIR."
