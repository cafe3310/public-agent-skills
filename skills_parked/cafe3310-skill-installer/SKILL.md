---
name: cafe3310-skill-installer
description: 自动化安装和更新来自 cafe3310 的所有 Agent Skills
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - bash
---

# 安装和更新 cafe3310 的所有 Agent Skill

此 Skill 用于帮助您自动化地下载、更新和维护来自 [cafe3310/public-agent-skills](https://github.com/cafe3310/public-agent-skills) 的所有技能。

## 🎯 核心功能

1. **一键同步**: 从 GitHub 仓库获取最新版本的 skills 到本地。
2. **安全更新**: 
   - 如果本地 `~/.agents/skills` 目录下已经存在由 `cafe3310` 创建的技能，它会自动覆盖更新到最新版。
   - 如果同名技能不是由 `cafe3310` 编写的，脚本会主动跳过，并提示您手动处理，防止误删您的自定义技能。
3. **状态预览**: 安装完成后，它会为您展示当前系统中所有可用技能的清单及其主要作用。

## 🚀 开发者指示 (Instructions)

如果你是一个 Agent，请执行以下步骤来协助用户完成安装：

1. **第一步：克隆并准备环境**  
   克隆 `https://github.com/cafe3310/public-agent-skills.git` 到临时目录。

2. **第二步：运行安装脚本**  
   定位到仓库中的 `skills/cafe3310-skill-installer/scripts/install.sh`，赋予其执行权限并运行它：
   ```bash
   chmod +x skills/cafe3310-skill-installer/scripts/install.sh
   bash skills/cafe3310-skill-installer/scripts/install.sh
   ```

3. **第三步：确认结果**  
   根据安装脚本输出的结果，向用户反馈安装成功的技能列表，并提醒用户哪些技能因为潜在冲突而被跳过（如果有）。

## 🛠 维护者
- **作者**: [cafe3310](https://github.com/cafe3310)
- **仓库地址**: `https://github.com/cafe3310/public-agent-skills`

---
> **小贴士**: 如果您是普通用户，只需将本文件交给您的 Agent 并说：“请帮我安装这里面提到的技能”，它就会为您处理好一切。
