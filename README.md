
## cafe3310's Public Agent Skills

个人常用的 Agent Skill（公开部分）。通过合适的上下文工程，可以将 Agent Skill 用在几乎任何地方。

### 提醒

Agent Skill 可能非常个性化，很多都是用户个人最佳实践的提炼，不一定对其他人有用。

这玩意儿说穿了是提示词和代码的集合。在当下，提示词也是代码。审核你放进本地 agent 的每一个 skill 的所有文档和代码，不要被人搞啦。

任何 LLM 相关的问题基本都是公开知识，学习如何使用 LLM 或让它协同你工作的方法里，最好的就是问 LLM 自己，最智障的是花钱买课。可以先问问 Gemini / GPT「这是我看到的文档，我希望学习关于 x 的知识。交互式地教教我」。

### 后续计划

工作和生活中自己不想做的麻烦事情基本会做成 Agent Skill 放在这里。

有计划认真给我猫制作 [咩咩和啾啾相册](https://github.com/cafe3310/miemie-jiujiu-album) ...

### 安装

#### 手动安装

在同时使用 `antigravity-cli`, `opencode`, `pi` 等不同 Agent 工具时，详尽的 skills 安装说明与最佳实践如下：

1. **原始文件保持在 git 目录**
2. **在 `~/.agents/skills` 目录放入软链接**，指向第 1 步中的 git 目录（供 `opencode`, `pi` 等工具使用）
3. **在 `~/.gemini/antigravity-cli/skills` 目录放入软链接**，指向第 1 步中的 git 目录（供 `antigravity-cli` 使用）

你可以克隆项目仓库后，直接运行以下脚本来自动完成上述软链接的配置：

```bash
chmod +x link_skills.sh
./link_skills.sh
```

该脚本会自动探测你系统中的 `~/.agents`、`~/.claude`、`~/.gemini/antigravity-cli` 和 `~/.gemini` 等目录，并自动在这些已存在的目录下创建 `skills` 软链接（若均不存在，则默认在 `~/.agents/skills` 和 `~/.gemini/antigravity-cli/skills` 中创建）。

#### 自动安装

向你的 Agent 发以下指令：

```plain
请先读取并按此文件的指示进行操作： https://raw.githubusercontent.com/cafe3310/public-agent-skills/main/skills/cafe3310-skill-installer/SKILL.md
```

记得先审核一下脚本做了什么。

### 一、创作与知识管理

这类 Skill 解决信息结构化、表达优化与知识复用问题。

适用于内容生产、研究分析及长期知识资产管理。

#### 深度研究 / [deep-research](skills/deep-research)

一个具备严谨性的多阶段深度研究方案。通过领域方法论机制，在展开具体研究前自动确立行业标准评估框架。随后，它动态编排多个 Subagent 深入网络挖掘关键数据点与对比指标，避免生成表面化的总结。它内置了基于交叉对比的饱和度测试，确保研究覆盖足够的维度、数据和来源，最终生成一篇有数据支撑的综合研究报告。

#### 语音转写长文处理 / [long-audio-transcript-processor](skills/long-audio-transcript-processor)

解决超长语音转写稿（如全天会议、深度访谈）无法一次性塞入上下文的难题。通过文件系统记录处理状态，支持分段校对、清洗与结构化，同时动态维护全局勘误和术语表，以确保前后文一致。支持「断点续传」，随时中断工作而不丢失进度，适合整理大规模录音稿。也能随语音处理满足额外的内容提炼、问答获取、角色识别等需求。

方便从自己身上提取知识。

#### 语音整理入库 / [long-audio-to-obsidian](skills/long-audio-to-obsidian)

专门用于将语音转写项目的复杂文件结构（原始录音、分段脚本、说明文档）整理并合并。它采用「Agent 规划与脚本执行相结合」的模式，产出适合在 Obsidian 归档的 Markdown。

#### IM 知识库整理 / [im-local-kb](skills/im-local-kb)

重型 IM 知识整理和分析技能，专注于从聊天记录中提取高价值的知识。它维护一个基于 Markdown 的本地文件系统，支持数据摄入、断档诊断和知识生成。可以处理上万行的大量群聊信息。

方便从网友身上提取知识。

#### IM Wiki 提取 / [im-wiki-extractor](skills/im-wiki-extractor)

用于从超长 IM 对话中增量提取结构化知识，并沉淀为可持续更新的 Wiki。通过滑动窗口处理、断点续传和来源追踪，避免一次性处理大体量聊天记录时的信息遗漏与上下文漂移。适合做长期群聊沉淀、项目复盘与事实查证。这个 Agent Skill 需要配合 [memories-off](https://github.com/cafe3310/agent-skill-memories-off) 工具使用。

#### 聊天记录项目化处理 / [long-chat-task-processor](skills/long-chat-task-processor)

专门用于处理按 Markdown 标题组织的超长聊天记录。它基于文档目录结构 (TOC) 进行分段分析，能够精准提取任务、决策和里程碑，并自动积累实体映射表（人名/概念），将其转化为结构化的项目管理资产，支持断点续传。

#### 网页/视频本地化剪藏 / [online-content-collector](skills/online-content-collector)

扫描 Obsidian 中带有 `#Marker-待下载` 的链接，用工具下载素材内容，并按 `[YYYY-MM-DD-HH] {分类} {描述}` 规范整理，实现自动化素材本地化。

#### 项目交互式学习 / [project-learner](skills/project-learner)

让 Agent 充当导师，在讲解项目代码或底层技术时，自动将过程记录到持久化的学习日志中。支持断点续学，让学习过程像项目开发一样有据可查。

#### 单文件沉浸式网页生成 / [oneshot-website](skills/oneshot-website)

一键生成高审美、全交互的单文件 HTML 网页。无需外部图片或构建步骤，仅通过 CSS 渐变、SVG 艺术和 Canvas API 提供高质量的视觉效果。适用于成果展示、AI 能力演示或创建令人惊叹的 CodePen 作品。
（来源：github/jpcaparas）

#### 深度调研生态合作规划 / [deep-research-partnership-planner](skills/deep-research-partnership-planner)

结合深度调研与人工洞察，为生态合作生成商业落地规划与颗粒度的宣发物料。通过严谨的两阶段调研（前期探索与深度研究）、引入人工战略判断，最终生成包含商业合作规划、早期预热方案及执行清单在内的全套 GTM 方案。强调「无调研不规划」，避免凭空编造，是进行业务合作的实用工具。

#### 产研宣发物料生成 / [tech-to-marketing-brief](skills/tech-to-marketing-brief)

充当产研侧与运营侧的「翻译官」。将冷冰冰的技术特性、算法指标通过痛点关联与风格重塑，转化为高颗粒度的运营 Brief、跨平台社媒宣发案例（小红书/公众号/X）以及配套的研发 Jira Ticket。确保技术卖点能精准转化为用户感知的心智，实现产研与营销的顺畅对接。

#### 笔记库查资料 / [obsidian-knowledge-filter](skills/obsidian-knowledge-filter)

面对庞大 Obsidian 知识库时，通过关键词定位相关笔记，自动提取上下文并综合生成专题报告。支持人工筛选介入，防止误关联。适合周期性复盘、跨笔记主题研究。

#### 待办事项整理 / [obsidian-todo-collector](skills/obsidian-todo-collector)

专门用于从 Obsidian 知识库中定期（如每周/每月）提取所有以 `🟥` 标记的未完成事件和规划性事项。它会自动生成一份结构化的汇总文档，追踪事项来源，并支持在后续处理中自动更新状态。

#### 标准化笔记编写 / [cafe3310-obsidian-writer](skills/cafe3310-obsidian-writer)

指导 Agent 编写符合个人知识库风格的文档。要求包含 YAML 元数据、标准化标签、溯源说明以及特定的 Emoji 语意规范，确保知识库的长期整洁与可检索性。

#### 内容语气调整 / [content-tone-adjuster](skills/content-tone-adjuster)

深度调整文本风格。内置用于消除 AI 刻板表达的「去模型味儿」模式和去除浮夸大词与宏大叙事的「平实务实化」模式。适用于将 AI 初稿转化为更自然、更务实的沟通文案或博客。

#### 写周报 / [weekly-report-writer](skills/weekly-report-writer)

自动化起草周报。通过综合指定日期范围内的每日日志、项目文档和上一份周报，自动识别进展、待办继承（未完成事项自动滚动到下周）和风险卡点，生成兼顾个人存档与团队汇报的分层报告。

### 二、在线平台 Agent 化

#### 部署到 ModelScope / [deploy-folder-to-modelscope](skills/deploy-folder-to-modelscope)

自动化 ModelScope 仓库发布流程：克隆目标仓库 → 复制指定子目录 → 提交带语义化信息的 commit → 推送远程。支持环境变量配置访问令牌。降低从实验到社区共享的发布成本。

#### Hugging Face 数据查询 / [hugging-face-stat](skills/hugging-face-stat)

专门用于获取 Hugging Face 上的模型、数据集和 Space 的详细统计信息。最核心的功能是能查询到网页端不直接展示的**历史总下载量**，并能分析 Space 的运行硬件规格，辅助进行竞品调研或热度评估。

#### Twitter 数据观察 / [twitter-watch](skills/twitter-watch)

收集一系列指定推文的互动数据。

### 三、项目管理与开发协作范式

定义可重复执行的开发流程与协作规范，提升模型在代码库中开发的效率和长期一致性。

可以按不同项目选择不同的范式。

#### 设计理念整理 / [project-design-concept-organizer](skills/project-design-concept-organizer)

专门用来提炼项目中的隐性知识。把分散的代码变更抽象为设计模式或协议规范，确保项目在复杂化过程中保持设计的一致性。

#### 文档模板提供 / [doc-template-provider](skills/doc-template-provider)

提供一系列标准化文档模板，涵盖项目基础规范 (`GEMINI.md`)、需求文档、缺陷跟踪、待办列表以及 Jira/Dima 需求单等，确保项目文档从起步阶段就具备专业且一致的结构。

#### Git 安全回退 / [git-snapshot-rollback](skills/git-snapshot-rollback)

在执行 `git reset --hard` 前自动将当前状态快照到存档分支，并在 `ARCHIVE.md` 中记录双向链接。确保回退操作安全且决策流可追溯。

#### 轻量版项目管理范式 / [doc-todo-log-loop](skills/doc-todo-log-loop)

作为轻量级默认开发循环，适用于无复杂流程的中小型项目。要求每项任务始于文档分析 → 生成 TODO 清单 → 开发后附加执行日志 → 提交前验证闭环。强调人的确认，最小化「想到哪做到哪」的不可控性，也防止自己忘掉。

#### 模型发布演示管理 / [release-showcase-manager](skills/release-showcase-manager)

针对 AI 模型发布的大规模演示项目管理框架。采用 `doc-todo-log-loop` 驱动，涵盖从模型能力研究、Scenario 设计、开发实施到录制笔记与性能评价的全生命周期。它是端到端的工程管理体系，不只是简单的素材整理。

#### 技能创造者 / [skill-creator](skills/skill-creator)

用于自动化地创建、测试和优化 Agent Skill 本身。它涵盖了从意图捕捉、SKILL.md 编写到并行测试、自动评分和描述优化（提升触发准确率）的全生命周期。当你发现自己在重复某种复杂的指令流时，用它将其「固化」为技能。

### 四、辅助工具

针对特定高频率、低创造性但易出错的机械性任务提供的专用解决方案。

#### 联系人/群组整理 / [im-contact-sorter](skills/im-contact-sorter)

针对缺少分类功能的 IM 软件。通过「截图-OCR-合并-分析」的流水线，识别未分类的项目并生成报告，辅助进行清理和资产归档。

#### 媒体库整理 / [media-organizer](skills/media-organizer)

处理多媒体资产时的命名与分类工具。基于文件元数据（拍摄时间）或图像内容分析，自动生成 `YYYY-MM-DD_项目_描述.png` 格式的文件名，并输出带缩略图的索引 README。适用于设计素材归档、用户反馈截图整理等场景。用于维护运营资产库。

#### 发布视频专业加工 / [showcase-video-processor](skills/showcase-video-processor)

协助制作高质量模型发布视频。通过 FFmpeg 实现无损裁剪（去除系统 UI）、智能变速（加速推理过程）、定格缩放等专业操作，并支持撰写多粒度（微观/中观/宏观）分镜策划文档，打造专业审美的演示集。

#### 做微信表情包 / [wx-emoji-maker](skills/wx-emoji-maker)

微信表情包批量生成工具。自动添加透明边框、调整至 240×240 像素、生成预览图包。

#### 使用本地 Claude 插件 / [use-claude-plugin](skills/use-claude-plugin)

检索并使用本地目录中的 Claude 插件完成特定任务。它能定位插件库中的专业技能，读取并遵循其 `SKILL.md` 指令，并模拟该插件的身份来执行任务。

#### 文本水印 / [text-watermark-fountain](skills/text-watermark-fountain)

基于喷泉码与句子长度操纵的文本隐写工具。娱乐向，并不是什么严谨方案。

#### 代码库术语审计 / [code-naming-auditor](skills/code-naming-auditor)

代码库术语一致性检查器。基于项目 Glossary 文件扫描变量/函数名，识别如 `getUserInfo()` 与 `fetchUserDetails()` 的命名冲突，输出重构建议。适合长期维护项目或微服务架构中保持领域语言统一。

#### 浏览器自动化工具 / [agent-browser](skills/agent-browser)

为 AI Agent 提供的快速浏览器自动化工具。通过 CDP 协议操作 Chrome/Chromium，支持无障碍树快照和紧凑的元素引用。适用于网页交互、导航及 Electron 应用自动化。
（来源：https://github.com/vercel-labs/agent-browser）

#### 产研级前端设计迭代 / [impeccable](skills/impeccable)

专业的产研级前端界面设计与迭代工具。支持从需求定义到代码实现的流程，专注于高审美的界面打磨、动画添加及优化。
（来源：https://github.com/pbakaus/impeccable）

#### 技能快速安装器 / [cafe3310-skill-installer](skills/cafe3310-skill-installer)

自动化安装和更新本仓库中所有技能的专用工具。支持安全检测（防止覆盖用户自定义的同名技能）和安装后的状态预览。

### 暂时不用的技能 (Parked Skills) / [skills_parked](skills_parked)

这里存放一些目前不活跃、由于架构调整或个人工作流程变化而暂时“停靠”的技能。它们依然具有参考价值，但在当前阶段不作为推荐的默认工具。

#### 完整版项目管理范式 / [project-management](skills_parked/project-management)

确立项目级基础规则：Monorepo 目录结构、文档命名规范（`YYYYMMDD-type-topic.md`）、Git 分支策略（feature/hotfix/release）、任务追踪机制（TODO 标签与状态流转），给项目仓库一个限定完全的开发范式。

#### TDD 驱动的工作流 / [tdd-dev-cycle](skills_parked/tdd-dev-cycle)

对代码质量有明确要求的场景启用。强制要求测试先行：输入/输出 definition → 编写测试用例 → 实现逻辑 → 验证覆盖率 → 修复边界条件。该流程虽增加初期成本，但显著减少后期 Debug 时间，尤其适用于复杂 SQL 或算法模块。

#### 基于浏览器的测试 / [browser-testing](skills_parked/browser-testing)

定义了一套不依赖重型框架的 E2E 测试流。测试用例写在 Markdown 里，通过截图和人工比对验证功能，结果存放在应用目录中作为凭证。

#### PMP 式迭代流程 / [pmp-dev-process](skills_parked/pmp-dev-process)

引入结构化的迭代流程：修订章程 → 规划确认 → 执行 → 验证。适用于开启新功能、进行重大变更或需要严谨记录的场景。

#### 研究报告编写 / [content-research-writer](skills_parked/content-research-writer)

用于撰写深度文章、技术文档或博客时。助手协助梳理大纲、交叉验证资料、管理引用链路，并在保持作者原始语气的基础上优化段落逻辑。与简单生成文本的工具不同，它强调协作式写作，避免“AI腔”泛滥。

#### PRD 撰写助手 / [prd-writer](skills_parked/prd-writer)

指导 Agent 以商业分析师和产品经理的角色，通过 7 步结构化工作流引导对话，将模糊的产品想法转化为详尽、可执行的产品需求文档 (PRD)。包含标准模板与现状分析流程。

#### 看看剪贴板图片 / [paste-image](skills_parked/paste-image)

打通 macOS 剪贴板与 LLM 分析管道的桥梁。运行后自动将剪贴板中的图片保存为本地 PNG 文件，并返回路径供后续 Skill 调用。适用于「截图给 Coding Agent 看看效果」的场景。
