
# cafe3310's Public Agent Skills

个人常用的 Agent Skill（公开部分）。通过合适的上下文工程，可以将 Agent Skill 用在几乎任何地方。

## 提醒

Agent Skill 可能非常个性化，很多都是用户个人最佳实践的提炼，不一定对其他人有用。

这玩意儿说穿了是提示词和代码的集合。在当下，提示词也是代码。审核你放进本地 agent 的每一个 skill 的所有文档和代码，不要被人搞啦。

任何 LLM 相关的问题基本都是公开知识，学习如何使用 LLM 或让它协同你工作的方法里，最好的就是问 LLM 自己，最智障的是花钱买课。可以先问问 Gemini / GPT「这是我看到的文档，我希望学习关于 x 的知识。交互式地教教我」。

为了让 Agent 能够正确识别每个 Skill 的依赖，这个仓库中的 `SKILL.md` Frontmatter 声明了以下扩展属性：

- `depends_on_skill`：这个 Agent Skill 运行依赖的其他 Agent Skill。
- `depends_on_binary`：这个 Agent Skill 运行依赖的其他程序（如 `ffmpeg`、`python3`）。

### 三方大型 Skill 集合的收敛方案（Composite Skill）

开源社区中的一些重型项目（如 `hyperframes`、`open-slide`、`blender-skills`）往往自带十几乃至二十几个细粒度 Skill。如果将它们直接平铺安装到 `~/.agents/skills` 或 `~/.gemini/config/skills`，不仅会挤占全局技能列表，还会把大量低频子技能的 description 常驻塞进 Agent 的初始上下文。

本仓库对这类三方大型 Skill 集合统一采用「复合技能路由器（Composite Skill Router）」结构进行二次封装：

- **单一顶层入口**：在 `skills/<suite-name>/SKILL.md` 中仅保留一个总控入口，聚合整个套件的触发条件、通用渲染/运行契约，以及一张按项目状态或任务意图匹配的路由表（Intent Routing Table）。
- **子技能下沉按需加载**：原仓库中的多个独立 Skill 统一收纳至 `skills/<suite-name>/subskills/<subskill-name>/SKILL.md`。Agent 仅在顶层路由命中具体任务时，才按相对路径读取对应的子技能文档与脚本，平时不占用全局命名空间。
- **内部互引路径归一化**：将上游各子技能文档之间原本假设平级安装的跨技能引用（如 `/slide-authoring`、`/hyperframes-cli`），统一改写为指向 `subskills/<name>/SKILL.md` 的相对文件引用，使整套技能在单目录内自洽运行。

## 后续计划

工作和生活中自己不想做的麻烦事情基本会做成 Agent Skill 放在这里。

有计划认真给我猫制作 [咩咩和啾啾相册](https://github.com/cafe3310/miemie-jiujiu-album) ...

## 安装

### 手动安装

在同时使用 `antigravity-cli`, `opencode`, `pi` 等不同 Agent 工具时，详尽的 skills 安装说明与最佳实践如下：

1. **原始文件保持在 git 目录**
2. **在 `~/.agents/skills` 目录物理拷贝同步**（支持差异比对与覆盖提示，供 `opencode`, `pi` 等工具使用）
3. **在 `~/.gemini/config/skills` 目录物理拷贝同步**（符合 Antigravity / Antigravity CLI 官方标准）

你可以克隆项目仓库后，直接运行以下脚本来自动完成安装与同步：

```bash
chmod +x link_skills.py
python3 link_skills.py
```

该脚本会自动探测你系统中的 `~/.agents`、`~/.claude` 和 `~/.gemini/config` 等目录，并在这些已存在的目录下执行物理技能目录的同步与拷贝。若目标目录中已存在且文件有修改，会交互式提示您确认覆盖（若均不存在，则默认在 `~/.agents/skills` 和 `~/.gemini/config/skills` 中创建并拷贝）。

此外，脚本在执行时，若目标目录下不存在 `agents.md`，它会自动在该目录下创建一个 `agents.md` 说明文件，指明这里的 skills 是复制自哪个本地物理仓库路径，提示在该工作区下编辑 skills 时应优先编辑源路径并重新运行 `link_skills.sh` 脚本；若目标目录下已存在该文件，则跳过生成。

### 自动安装

向你的 Agent 发以下指令：

```plain
请先读取并按此文件的指示进行操作： https://raw.githubusercontent.com/cafe3310/public-agent-skills/main/skills_parked/cafe3310-skill-installer/SKILL.md
```

记得先审核一下脚本做了什么。

## Skill 列表

### 一、项目管理

提供方法论和迭代范式，以协助项目管理。

#### 规范驱动与日志协作范式 / [guide](skills/guide)

基于规范驱动与日志记录的轻量级人机协作项目开发与管理方案，包含 `/guide load`、`/guide spec`、`/guide handoff`、`/guide test`、`/guide log` 子命令。用户控制开发节奏，Agent 负责文档撰写、任务拆分、开发执行和日志记录。

#### 面向切面的产品策划与需求拆解 / [aop-product-planner](skills/aop-product-planner)

面向切面 (AOP) 的产品工程策划与需求拆解范式。覆盖从目标叙事、AOP 切面分层、乱序 Idea 收集、功能边界界定到需求依赖拓扑、复杂度估算与可交互网页面板预览的完整规划流程。

#### 项目极简进度汇总 / [cafe-whatabout](skills/cafe-whatabout)

检索 Obsidian 知识库中关于目标项目的最新记录，快速输出包含目标与交付物、关键时间节点、当前现状、上下游依赖及下一步动作的极简进度汇总。

#### 轻量版项目管理范式 / [doc-todo-log-loop](skills_parked/doc-todo-log-loop)

作为轻量级默认开发循环，适用于无复杂流程的中小型项目。要求每项任务始于文档分析 → 生成 TODO 清单 → 开发后附加执行日志 → 提交前验证。强调人的确认，最小化「想到哪做到哪」的不可控性，也防止自己忘掉。

#### 设计理念整理 / [project-design-concept-organizer](skills/project-design-concept-organizer)

专门用来提炼项目中的隐性知识。把分散的代码变更抽象为设计模式或协议规范，确保项目在复杂化过程中保持设计的一致性。

### 二、专业工具

对特定领域任务的专业工具或工作流。

#### 交互式学习助手 / [learning-assistant](skills/learning-assistant)

交互式的主题学习助手。它能将您的学习目标进行结构化拆解，并通过高频读写本地知识图谱（memocli/memories-off）来记录、追踪学习状态，以交互问答的方式引导完成整个概念或主题的学习过程。

#### 做微信表情包 / [wx-emoji-maker](skills/wx-emoji-maker)

微信表情包批量生成工具。自动添加透明边框、调整至 240×240 像素、生成预览图包。

#### macOS 规范图标生成 / [icns-maker](skills/icns-maker)

将 PNG 图标转换为符合 macOS Big Sur+ 视觉规范的 `.icns` 文件。自动将全出血主体缩放至 824×824 像素并补齐透明安全留白（Padding），生成标准 10 阶分辨率 `.iconset` 并通过 `iconutil` 打包，避免图标在 Dock 和 Finder 中视觉过大。

#### 浏览器自动化工具 / [agent-browser](skills/agent-browser)

为 AI Agent 提供的快速浏览器自动化工具。通过 CDP 协议操作 Chrome/Chromium，支持无障碍树快照和紧凑的元素引用。适用于网页交互、导航及 Electron 应用自动化。
（来源：https://github.com/vercel-labs/agent-browser）

#### 移动端模拟器自动化工具 / [sim-use](skills_parked/sim-use)

为 AI Agent 提供的 iOS 模拟器和 Android 模拟器/真机屏幕操作与自动化工具。支持在设备上进行点击、滑动、输入、屏幕截图及 UI 描述，适用于自动化测试或移动端应用交互。
（来源：https://github.com/lycorp-jp/sim-use）

#### 产研级前端设计迭代 / [impeccable](skills/impeccable)

专业的产研级前端界面设计与迭代工具。支持从需求定义到代码实现的流程，专注于高审美的界面打磨、动画添加及优化。
（来源：https://github.com/pbakaus/impeccable）

#### HyperFrames 视频渲染与动效开发套件 / [hyperframes](skills/hyperframes)

基于 Web 技术（HTML/CSS/JS/Canvas）编写、由浏览器内核与 FFmpeg 驱动的确定性视频与动画渲染框架。采用复合技能架构（Composite Skill），包含主技能渲染契约、14 套内置视觉预设、7 大视频形态规范及 6 个专项子技能（`hyperframes-cli`、`hyperframes-registry`、`media-use`、`slideshow`、`remotion-to-hyperframes`、`figma`）。
（来源：https://github.com/heygen-com/hyperframes）

#### Open-Slide 幻灯片开发套件 / [openslide](skills/openslide)

基于 React 与 1920×1080 确定性画布的幻灯片演示（Slide Deck）开发套件。采用复合技能架构（Composite Skill），包含 5 个专项子技能：`create-slide`（Deck 策划与初始化）、`slide-authoring`（画布排版、垂直预算、分步揭示、Magic Move 形变与讲稿导出）、`current-slide`（实时游标定位）、`apply-comments`（浏览器 Inspector 批注应用）与 `create-theme`（可复用主题包构建）。
（来源：https://github.com/1weiho/open-slide）

#### Blender 3D 产品摄影与自动化套件 / [blender-skills](skills/blender-skills)

基于 Blender MCP 与开源资产的 3D 产品级自动化开发套件。采用复合技能架构（Composite Skill），包含 14 个专项子技能：PolyHaven 摄影棚与 PBR 材质赋予、多材质轮换对比渲染、6 种电影级运镜动画（环绕、慢推、推进旋转、摇臂等）带透明通道压制、模型表面高光打磨、Three.js 交互式 Web 3D 导出以及底层 WebSocket 控制。
（来源：https://github.com/kevinbadi/blender-skills）

### 三、开发辅助

对日常代码开发与版本控制过程的辅助。

#### 跨会话任务交接 / [handoff](skills_parked/handoff)

编写或更新交接文档，以便拥有全新上下文的下一个 Agent 可以继续此项工作。它会基于当前进展、目标（包括当前 TODO 文件）、近期尝试（已生效/未生效方案）、推荐技能以及后续步骤，在项目根目录下生成或更新 `HANDOFF.md`。支持根据传入参数定制任务焦点，并生成一段可供用户在全新 Agent 对话中一键粘贴的交接指令，实现快速交接与断点续传。

#### Claude Code 任务接续 / [claude-code-handoff](skills_parked/claude-code-handoff)

解析本地 Claude Code CLI 会话的 `.jsonl` 文件，根据会话线索合成交接文档，并生成接续指令，帮助新 Agent 从 Claude Code 停下的断点继续工作。

#### Git 安全回退 / [git-snapshot-rollback](skills/git-snapshot-rollback)

在执行 `git reset --hard` 前自动将当前状态快照到存档分支，并在 `ARCHIVE.md` 中记录双向链接。确保回退操作安全且决策流可追溯。

#### 互动式人类审阅 / [interactive-human-review](skills/interactive-human-review)

在大范围变更后引导用户进行渐进式互动审阅与理解确认。维护一个运行中的 checklist 并在关键节点通过提问测验、交互重述，确保用户深度掌握了修改的动机、逻辑与影响。

### 四、特定工作项目仓库式管理

需要控制一个专有仓库的重型工作流，常用于长期持续的特定目的项目。

#### IM 知识库整理 / [im-local-kb](skills_parked/im-local-kb)

重型 IM 知识整理和分析技能，专注于从聊天记录中提取高价值的知识。它维护一个基于 Markdown 的本地文件系统，支持数据摄入、断档诊断和知识生成。可以处理上万行的大量群聊信息。

方便从网友身上提取知识。

#### 媒体库整理 / [media-organizer](skills/media-organizer)

处理多媒体资产时的命名与分类工具。基于文件元数据（拍摄时间）或图像内容分析，自动生成 `YYYY-MM-DD_项目_描述.png` 格式的文件名，并输出带缩略图的索引 README。适用于设计素材归档、用户反馈截图整理等场景。用于维护运营资产库。

### 五、创作和内容编写

用于编写多种内容。

#### 文档模板提供 / [doc-template-provider](skills/doc-template-provider)

提供一系列标准化文档模板，涵盖项目基础规范 (`GEMINI.md`)、需求文档、缺陷跟踪、待办列表以及 Jira 需求单等，确保项目文档从起步阶段就具备专业且一致的结构。

#### 写周报 / [weekly-report-writer](skills/weekly-report-writer)

自动化起草周报。通过综合指定日期范围内的每日日志、项目文档和上一份周报，自动识别进展、待办继承（未完成事项自动滚动到下周）和风险卡点，生成兼顾个人存档与团队同步的报告。

#### 标准化笔记编写 / [cafe3310-obsidian-writer](skills_parked/cafe3310-obsidian-writer)

指导 Agent 编写符合个人知识库风格的文档。要求包含 YAML 元数据、标准化标签、溯源说明以及特定的 Emoji 语意规范，确保知识库的长期整洁与可检索性。

#### 内容语气调整 / [content-tone-adjuster](skills/content-tone-adjuster)

深度调整文本风格。内置用于消除 AI 刻板表达的「去模型味儿」模式和去除浮夸大词与宏大叙事的「平实务实化」模式。适用于将 AI 初稿转化为更自然、更务实的沟通文案或博客。

### 六、内容处理和转换

对已有内容进行转换、整理、提取。

#### 语音转写长文处理 / [long-audio-transcript-processor](skills_parked/long-audio-transcript-processor)

解决超长语音转写稿（如全天会议、深度访谈）无法一次性塞入上下文的难题。通过文件系统记录处理状态，支持分段校对、清洗与结构化，同时动态维护全局勘误和术语表，以确保前后文一致。支持「断点续传」，随时中断工作而不丢失进度，适合整理大规模录音稿。也能随语音处理满足额外的内容提炼、问答获取、角色识别等需求。

方便从自己身上提取知识。

#### 语音整理入库 / [long-audio-to-obsidian](skills_parked/long-audio-to-obsidian)

专门用于将语音转写项目的复杂文件结构（原始录音、分段脚本、说明文档）整理并合并。它采用「Agent 规划与脚本执行相结合」的模式，产出适合在 Obsidian 归档的 Markdown。

#### 面试记录处理 / [interview-processor](skills_parked/interview-processor)

处理面试前后的一系列记录。输入面试记录(转写)、面试官笔记、岗位信息、简历；在面试前规划面试大纲，在面试后提取真实提问、规范化问题、生成结构化的面试纪要与专家级面试官自评。它支持配合 `memories-off` 技能，将生成的数据作为实体沉淀到本地知识图谱。

#### 群聊录屏提取记录 / [chat-screenrec-extractor](skills/chat-screenrec-extractor)

将包含一系列群聊滚屏录制的视频转化为分群归档的 Markdown 聊天记录。支持通过 Web UI 交互式调整切帧采样周期并拖拽标定群标题栏与消息正文区 ROI，调用 macOS 原生 Apple Vision OCR 进行硬件加速文字坐标提取，结合垂直滚动位移时序算法自动剔除重叠冗余并合并生成规范聊天文档。

### 七、信息收集和本地化

从网络或外部数据源中进行信息获取或本地化。

#### 深度研究 / [deep-research](skills_parked/deep-research)

一个具备严谨性的多阶段深度研究方案。通过领域方法论机制，在展开具体研究前自动确立行业标准评估框架。随后，它动态编排多个 Subagent 深入网络挖掘关键数据点与对比指标，避免生成表面化的总结。它内置了基于交叉对比的饱和度测试，确保研究覆盖足够的维度、数据和来源，最终生成一篇有数据支撑的综合研究报告。

#### 网页/视频本地化剪藏 / [online-content-collector](skills/online-content-collector)

扫描 Obsidian 中带有 `#Marker-待下载` 的链接，用工具下载素材内容，并按 `[YYYY-MM-DD-HH] {分类} {描述}` 规范整理，实现自动化素材本地化。

#### Twitter 数据观察 / [twitter-watch](skills_parked/twitter-watch)

收集一系列指定推文的互动数据。

#### 网页/文件转 Markdown / [markdown-new](skills/markdown-new)

通过 markdown.new API，将网页 URL、本地文件、整站爬取或网页搜索结果转换为干净、低 Token 的 Markdown。

### 八、偶尔使用的 Skill - [skills_parked](skills_parked)

偶尔要用，但没必要保持开启的 Agent Skill。

#### 技能快速安装器 / [cafe3310-skill-installer](skills_parked/cafe3310-skill-installer)

自动化安装和更新本仓库中所有技能的专用工具。支持安全检测（防止覆盖用户自定义的同名技能）和安装后的状态预览。

#### 代码库术语审计 / [code-naming-auditor](skills_parked/code-naming-auditor)

代码库术语一致性检查器。基于项目 Glossary 文件扫描变量/函数名，识别如 `getUserInfo()` 与 `fetchUserDetails()` 的命名冲突，输出重构建议。适合长期维护项目或微服务架构中保持领域语言统一。

#### 调研生态合作规划 / [deep-research-partnership-planner](skills_parked/deep-research-partnership-planner)

结合深度调研与人工洞察，为生态合作生成商业落地规划与宣发物料。通过两阶段调研（前期探索与深度研究）与人工判断，生成包含商业合作规划、早期预热方案及执行清单在内的 GTM 方案。强调「无调研不规划」，避免凭空编造。

#### 部署到 ModelScope / [deploy-folder-to-modelscope](skills_parked/deploy-folder-to-modelscope)

自动化 ModelScope 仓库发布流程：克隆目标仓库 → 复制指定子目录 → 提交带语义化信息的 commit → 推送远程。支持环境变量配置访问令牌。降低从实验到社区共享的发布成本。

#### Hugging Face 数据查询 / [hugging-face-stat](skills_parked/hugging-face-stat)

专门用于获取 Hugging Face 上的模型、数据集和 Space 的详细统计信息。最核心的功能是能查询到网页端不直接展示的**历史总下载量**，并能分析 Space 的运行硬件规格，辅助进行竞品调研或热度评估。

#### 联系人/群组整理 / [im-contact-sorter](skills_parked/im-contact-sorter)

针对缺少分类功能的 IM 软件。通过「截图-OCR-合并-分析」的流水线，识别未分类的项目并生成报告，辅助进行清理和资产归档。

#### IM Wiki 提取 / [im-wiki-extractor](skills_parked/im-wiki-extractor)

用于从超长 IM 对话中增量提取结构化知识，并沉淀为可持续更新的 Wiki。通过滑动窗口处理、断点续传和来源追踪，避免一次性处理大体量聊天记录时的信息遗漏与上下文漂移。适合做长期群聊沉淀、项目复盘与事实查证。这个 Agent Skill 需要配合 [memories-off](https://github.com/cafe3310/agent-skill-memories-off) 工具使用。

#### 聊天记录项目化处理 / [long-chat-task-processor](skills_parked/long-chat-task-processor)

专门用于处理按 Markdown 标题组织的超长聊天记录。它基于文档目录结构 (TOC) 进行分段分析，能够精准提取任务、决策和里程碑，并自动积累实体映射表（人名/概念），将其转化为结构化的项目管理资产，支持断点续传。

#### 笔记库查资料 / [obsidian-knowledge-filter](skills_parked/obsidian-knowledge-filter)

面对庞大 Obsidian 知识库时，通过关键词定位相关笔记，自动提取上下文并综合生成专题报告。支持人工筛选介入，防止误关联。适合周期性复盘、跨笔记主题研究。

#### 待办事项整理 / [obsidian-todo-collector](skills_parked/obsidian-todo-collector)

专门用于从 Obsidian 知识库中定期（如每周/每月）提取所有以 `🟥` 标记的未完成事件和规划性事项。它会自动生成一份结构化的汇总文档，追踪事项来源，并支持在后续处理中自动更新状态。

#### 单文件沉浸式网页生成 / [oneshot-website](skills_parked/oneshot-website)

一键生成高审美、全交互的单文件 HTML 网页。无需外部图片或构建步骤，仅通过 CSS 渐变、SVG 艺术和 Canvas API 提供高质量的视觉效果。适用于成果展示、AI 能力演示或创建令人惊叹的 CodePen 作品。
（来源：github/jpcaparas）

#### 使用本地 Claude 插件 / [use-claude-plugin](skills_parked/use-claude-plugin)

检索并使用本地目录中的 Claude 插件完成特定任务。它能定位插件库中的专业技能，读取并遵循其 `SKILL.md` 指令，并模拟该插件的身份来执行任务。

#### 项目交互式学习 / [project-learner](skills_parked/project-learner)

让 Agent 充当导师，在讲解项目代码或底层技术时，自动将过程记录到持久化的学习日志中。支持断点续学，让学习过程像项目开发一样有据可查。

#### Skill Creator / [skill-creator](skills_parked/skill-creator)

用于自动化地创建、测试和优化 Agent Skill 本身。它涵盖了从意图捕捉、SKILL.md 编写到并行测试、自动评分和描述优化（提升触发准确率）的全生命周期。当你发现自己在重复某种复杂的指令流时，用它将其「固化」为技能。

#### 文本水印 / [text-watermark-fountain](skills_parked/text-watermark-fountain)

基于喷泉码与句子长度操纵的文本隐写工具。娱乐向，并不是什么严谨方案。

#### 视频转表情包 GIF / [gemini-omni-video-to-sticker-gif](skills_parked/gemini-omni-video-to-sticker-gif)

利用多模态模型定位视频中的情绪动作区间，结合 FFmpeg 自动裁剪、移除背景并生成带透明通道的 240×240 表情包 GIF。

#### 自媒体大纲与语料管理 / [kol-writer](skills_parked/kol-writer)

梳理文章大纲与写作语料的管理流程。支持观点速记、结构化大纲梳理、补充检索与参考案例归档。

#### 设计风格演示站生成 / [llm-demo-website](skills_parked/llm-demo-website)

结合设计风格检索与前端组件规范，生成单页面 HTML 设计系统与组件演示页面。

#### 桌面端 Computer Use 自动化 / [open-computer-use](skills_parked/open-computer-use)

面向桌面环境的 GUI 自动化与系统操作辅助工具。

#### 学科结构化学习助手 / [subject-learning-assistant](skills_parked/subject-learning-assistant)

结合本地知识图谱（`memories-off`）构建概念分层结构，跟踪学习计划与学习日志。

### 九、已存档的 Skill - [skills_archived](skills_archived)

由于流程更迭、工具替代等原因，仅供参考的存档 Skill。

#### 完整版项目管理范式 / [project-management](skills_archived/project-management)

确立项目级基础规则：Monorepo 目录结构、文档命名规范（`YYYYMMDD-type-topic.md`）、Git 分支策略（feature/hotfix/release）、任务追踪机制（TODO 标签与状态流转），给项目仓库一个限定完全的开发范式。

#### TDD 驱动的工作流 / [tdd-dev-cycle](skills_archived/tdd-dev-cycle)

对代码质量有明确要求的场景启用。强制要求测试先行：输入/输出 definition → 编写测试用例 → 实现逻辑 → 验证覆盖率 → 修复边界条件。该流程虽增加初期成本，但显著减少后期 Debug 时间，尤其适用于复杂 SQL 或算法模块。

#### 基于浏览器的测试 / [browser-testing](skills_archived/browser-testing)

定义了一套不依赖重型框架的 E2E 测试流。测试用例写在 Markdown 里，通过截图和人工比对验证功能，结果存放在应用目录中作为凭证。

#### PMP 式迭代流程 / [pmp-dev-process](skills_archived/pmp-dev-process)

引入结构化的迭代流程：修订章程 → 规划确认 → 执行 → 验证。适用于开启新功能、进行重大变更或需要严谨记录的场景。

#### 研究报告编写 / [content-research-writer](skills_archived/content-research-writer)

用于撰写深度文章、技术文档或博客时。助手协助梳理大纲、交叉验证资料、管理引用链路，并在保持作者原始语气的基础上优化段落逻辑。与简单生成文本的工具不同，它强调协作式写作，避免“AI腔”泛滥。

#### PRD 撰写助手 / [prd-writer](skills_archived/prd-writer)

指导 Agent 以商业分析师和产品经理的角色，通过 7 步结构化工作流引导对话，将模糊的产品想法转化为详尽、可执行的产品需求文档 (PRD)。包含标准模板与现状分析流程。

#### 看看剪贴板图片 / [paste-image](skills_archived/paste-image)

打通 macOS 剪贴板与 LLM 分析管道的桥梁。运行后自动将剪贴板中的图片保存为本地 PNG 文件，并返回路径供后续 Skill 调用。适用于「截图给 Coding Agent 看看效果」的场景。
