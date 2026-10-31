---
title: Loop Engineering：如何为Agent设计流水线
platform: 小红书
style: 科普+干货
---

# Loop Engineering：如何为Agent设计流水线

6月7日，Google AI总监Addy Osmani定义了一个新概念：Loop Engineering。
定义只有一句话：“把你从那个提示AI的人的位置上替换掉。”

Loop 为什么会火？过去一周多个大佬都在不约而同的讨论Loop 。
Boris Cherny，Claude Code的技术负责人：“我不再给Claude写提示词了，我写Loop，Loop自己来完成工作。”
Peter Steinberger，龙虾之父：“你不应该使用提示词指挥Agent，而应该设计Loop来提示你的Agent。”
Andrej Karpathy，vibe coding提出者：“你必须把自己在Loop中移出去。”

大厂工程师、独立开发者、AI研究员，三个人从完全不同的地方出发，走到了同一个判断上。
本期带来分享，帮你一文读懂Loop Engineering。

1️⃣从Prompt 到 Loop
2️⃣ Loop的五个核心模块
3️⃣一个Loop跑起来是什么样
4️⃣咸味教训
5️⃣Loop的三个陷阱

#ai #LoopEngineering  #互联网大厂 #科技前沿与未来#程序员  #产品经理 #大模型 #转码 #小红书科技AMA  #领域驱动设计

猜你想搜
Loop Engineering
--- 📌 XHS_POST_TEXT_AND_DETAIL_DELIMITER 📌 ---
### Loop Engineering：如果你还在写提示词，那你已经落后了

作者：奇点日记
◎ 全文3334字｜阅读需11分钟

6月7日，Google AI总监Addy Osmani定义了一个新概念：Loop Engineering。
定义只有一句话：“把你从那个提示AI的人的位置上替换掉。”

Loop 为什么会火？过去一周多个大佬都在不约而同的讨论Loop。
Boris Cherny，Claude Code的技术负责人：“我不再给Claude写提示词了，我写Loop，Loop自己来完成工作。”
Peter Steinberger，龙虾之父：“你不应该使用提示词指挥Agent，而应该设计Loop来提示你的Agent。”
Andrej Karpathy，vibe coding提出者：“你必须把自己在Loop中移出去。”

大厂工程师、独立开发者、AI研究员，三个人从完全不同的地方出发，走到了同一个判断上。
继续看，你就会明白，为什么Loop这么重要。

---

### 1️⃣ 从 Prompt 到 Loop

过去两年，用AI的方式一直没变：你写一段 prompt，AI回复，你再写一段，它再回，一问一答，你始终握着方向盘。

这条路上有几个路标：
* **Prompt Engineering** —— 怎么把指令写得更精确。
* **Context Engineering** —— 怎么把上下文塞得更充分。
* **Harness Engineering** —— 怎么给AI搭一个运行环境。

每个阶段都在回答“怎么更好地告诉AI做什么”，
而 **Loop Engineering** 换了一个问题：从“怎么告诉AI做什么”变成了“怎么设计一个系统，让它自己知道做什么”。

区别在哪？Google AI总监Addy Osmani打了一个比方：
Loop Engineering在Harness Engineering更上一层，Harness是给一个AI搭环境，Loop是给一群AI搭一条流水线，还自带时钟和质检。

Pulumi的工程师Engin Diri说得更直白：一个Loop其实是两个循环嵌套在一起：内层对着规格说明干活，外层决定下一个规格说明应该是什么。

Boris把这种变化叫做“认知跃迁”。
* **第一次跃迁**：源代码不再是直接操作的对象。
  Boris：“我们不再写代码，而是给一个Agent下指令，它去调别的Agent，那个Agent又调更多Agent，像一棵成千上万个Agent组成的树。”
* **第二次跃迁**：Agent不再是直接对话的对象。
  Boris：“我不再跟Agent直接对话了，我跟Loop说话，或者跟Routine说话，它来替我调度Agent，Agent再去写代码。”

两次跃迁指向同一个方向：人一步一步往后退，从执行者变成指挥者，再从指挥者变成设计者。

---

### 2️⃣ Loop的五个核心模块

Google AI总监 Addy Osmani 定义了 Loop 的五个核心模块：

#### 1. Automations（心跳）
Automations是让Loop成为循环的东西。没有它，你只是手动跑了一次任务。Automations可以按时触发，自动发现和分拣任务。
Claude Code里你可以用 `/loop` 设定时任务，用 cron 排程，用 hooks 在 Agent 生命周期的特定节点触发，或者推到 GitHub Actions 上让它在关了电脑之后继续跑。
还有一个更接近Loop本质的命令 —— `/goal`：你给一个可验证的条件，比如“`auth/` 目录下所有测试通过且 lint 干净”，Agent会一直跑到条件满足为止，每跑一轮都由一个单独的小模型检查是否达标，写代码的Agent不是给自己打分的那个。

#### 2. Worktrees（防撞墙）
如果你同时跑多个Agent，它们可能操作同一个文件，就像两个工程师抢同一行代码一样，互相踩脚。
而 Worktree 是共享同一份仓库历史的独立工作目录，每个Agent在自己的分支上干活，互相碰不到。Worktree 实现了多个Agent并行跑，每人一个独立 git 分支，Codex 和 Claude Code 都支持 Worktree。

#### 3. Skills（记忆芯片）
Skill就是一个文件夹，里面放着 `SKILL.md` —— 项目规范、构建步骤、历史决策。Agent在执行任务时，每次都读 `SKILL.md`。
没有Skill，Loop每跑一轮都在从零推导你的整个项目；有了Skill，知识像复利一样累积。
Codex用 `$skill-name` 调用，Claude Code也会在任务匹配时自动调用。
Addy管这叫“意图的外化”（intent externalized）—— 意图只写一次，不再每轮重复。

#### 4. Connectors（手臂）
基于 MCP 协议，让 AI 接入真实世界：读 issue tracker、查数据库、调 staging API、发 Slack 消息。
Connectors 是 Loop 从“建议机器”变成“执行机器”的关键。没有 Connectors 的 Agent 只能说“这是修复方案”；有 Connectors 的 Loop 能自己开 PR、关联工单、CI 绿了自动 ping 频道。

#### 5. Sub-agents（制衡机制）
写代码的 Agent 永远给自己打高分，所以要有另一个裁判 Agent 制衡。
Sub-agent 用不同的指令、不同的模型，专门挑第一个 Agent 自洽但其实有问题的地方。
分工通常是：一个探索，一个实现，一个对着 spec 验收。
Addy说“Sub-agents是整个Loop里最有用的结构设计”。当你离开循环之后，唯一让你放心的是有一个独立的检查者。

---

### 3️⃣ 一个Loop跑起来是什么样

把五个核心模块拼在一起，一个完整的Loop是这样 ——

每天早上，Automations自动触发。它调用 triage skill 读取昨天的 CI 失败、新开的 issue、最近的 commit，把发现写入 Linear 看板。
对于每一条值得处理的 finding，Loop 自动开一个隔离 worktree，派 Sub-agent A 起草修复，再派 Sub-agent B 对着项目 skill 和已有测试做 review。
Connectors 让 Loop 自动开 PR、更新 ticket，CI 通过后 ping 频道通知。
Loop 自己搞不定的，推进人工 Triage 收件箱等你处理。

你设计了一次 Loop 流水线，之后你不需要 prompt 任何一个步骤。

Cameron Westland 是一个实际跑 Loop 的人，他分享了六个正在运行的 Loop：
* 有看着 PR 的，提交后自动盯着 CI 和 review，过了就合并，卡了就找人。
* 有跑实验的，让 AI 自己测 prompt 改动，同时跑三四个对照组。
* 最有趣的是拍视频的：AI 做完功能后自己写 Playwright 脚本录制操作过程，然后看自己的视频检查有没有 UI 问题。Cameron 说了他以前手动录 QuickTime 视频给 AI 看，有一天忍不住想：为什么我在替你做 QA？

Cameron 总结了一条发现 Loop 的方法：
“找到你正在手动做的反馈步骤：那个你在复制粘贴的 review，那个你在手动拖的视频，那个你每天早上重新读的 backlog，然后把它接成自动的 Loop。”

---

### 4️⃣ 咸味教训

AI 研究里有一条著名的原则叫 Bitter Lesson（苦味教训），Rich Sutton 在 2019 年提出：不要用人类的知识去设计 AI 系统，因为算力增长最终会让通用的、可扩展的方法碾压一切手工作品。历史一次又一次证明，直接让 AI 用更多算力学，比人类精心设计的方法更好。

Loop Engineering 有了自己的版本。AI News 的编辑把它叫 **Salty Lesson（咸味教训）**：
“不要自己去解决问题，而要把注意力放在能随 Agent 数量扩展系统设计上。例如，目标设定和编排调度。”

这个咸味教训有两面：
* 一面是“往下走” —— 当循环出问题的时候，你要能钻进去修，可靠性需要你能够降级。
* 另一面是“往上走” —— 当模型更强的时候，你要能退得更高，设计更大的 Loop。

Karpathy 走得更极端，他的 Autoresearch 项目让 AI 自己做研究：AI 自己提出假设，自己设计实验，自己跑，自己看结果，自己决定下一步。人只做一件事：在开始的时候，把目标设好。

Karpathy：“要想充分利用现在这些 AI 工具，你必须把自己从瓶颈中移出去。你不可能一直在那里提示下一个东西。你需要让自己退出循环。你必须让事情完全自主运行。”
Karpathy：“我不想做那个在循环中看结果的研究员，我在拖系统的后腿。所以问题是，我该怎么重构所有的抽象层，让我不在里面。我只需要安排一次，然后按下开始。”

Autoresearch 项目结果如何？跑了 48 小时，进行 700 次迭代，就有 20 个有效改进。这不是人在写代码，甚至不是人在提示 AI 写代码，是人在设计一个系统让 AI 自己迭代。

Karpathy 说这还只是开始：“现在的游戏规则，就是提高你的杠杆率。人类每多退出一个循环，AI就多跑一步。”

---

### 5️⃣ Loop的三个陷阱

Addy Osmani 在定义 Loop 的同时，也提出了三个潜在陷阱：

#### ① 验证盲区
Loop 无人值守地跑着，也在无人值守地犯错。你把“写代码”和“检查的”拆成两个子agent，是为了让 Loop 更严谨地说“Done”。“Done”是 Loop 的声明，而不是任务完成的证明。
Addy 反复强调一句话：“你的工作是发布你确认能跑的代码，不是发布 Loop 说能跑的代码。”验证仍然是你自己的事，人是最后的兜底逻辑。

#### ② 理解负债
Loop 替你写代码越快，“仓库里有什么”和“你真正懂什么”之间的裂缝就越大。
Addy 说：“顺畅的 Loop 只会让理解负债长得更快，除非你去读 Loop 产出的东西。”
Cameron Westland 也说了类似的话：“有些工作套上 Loop 只会更糟，比如战略，战略没有测试套件。如果你的收获是‘给所有事情套 Loop’，结果往往会跑偏。”
代码不是你写，但出问题你得能修，如果你连代码长什么样都不看，就是在给自己挖坑。

#### ③ 认知投降
Loop 自己跑起来之后，特别容易进入一种舒服状态：不再有意见，Loop 给什么就接什么。Addy 管这叫“认知投降” ——
Addy：“你带着判断力去设计Loop，那它就是解药；如果你设计Loop是为了不用动脑子，那它就是毒药。”

Addy 最后写了一句忠告：
“两个人建一模一样的 Loop，结果可能完全相反。一个用它加速自己深度理解工作，另一个用它逃避理解工作本身。Loop 分不出区别，但你知道。”

---

以上，既然看到这里了，如果觉得还不错，就顺手点个赞吧，如果想第一时间收到推送，可以点点关注啦~
谢谢你看我的文章，祝好，我们下次再见。

作者：奇点日记
