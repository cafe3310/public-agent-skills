
## cafe3310's Public Agent Skills

个人常用的 Agent Skill（公开部分）。通过合适的上下文工程，可以将 Agent Skill 用在几乎任何地方。

### 提醒

Agent Skill 可能非常个性化，很多都是用户个人最佳实践的提炼，不一定对其他人有用。

这玩意儿说穿了是提示词和代码的集合。在当下，提示词也是代码。审核你放进本地 agent 的每一个 skill 的所有文档和代码，不要被人搞啦。

任何 LLM 相关的问题基本都是公开知识，学习如何使用 LLM 或让它协同你工作的方法里，最好的就是问 LLM 自己，最智障的是花钱买课。可以先问问 Gemini / GPT「这是我看到的文档，我希望学习关于 x 的知识。交互式地教教我」。

### 安装

可以 clone 项目仓库并运行以下脚本：

```bash
chmod +x link_skills.sh
./link_skills.sh
```

该脚本会将 `skills/` 目录下的所有子目录符号链接到 `$HOME/.gemini/skills/`。

### 一、创作与知识管理

这类 Skill 解决信息结构化、表达优化与知识复用问题。

适用于内容生产、研究分析及长期知识资产管理。

#### 语音转写长文处理 / [long-audio-transcript-processor](skills/long-audio-transcript-processor)

解决超长语音转写稿（如全天会议、深度访谈）无法一次性塞入上下文的难题。通过文件系统记录处理状态，支持分段校对、清洗与结构化，同时动态维护全局勘误和术语表，以确保前后文一致。最重要的是支持「断点续传」，随时中断工作而不丢失进度，是整理录音稿的重型武器。也能随语音处理满足额外的内容提炼、问答获取、角色识别等需求，方便你蒸馏自己。

#### 语音整理入库 / [long-audio-to-obsidian](skills/long-audio-to-obsidian)

专门用于将语音转写项目的复杂文件结构（原始录音、分段脚本、说明文档）整理并合并。它采用「Agent 规划排序 + 脚本机械执行」的模式，产出适合在 Obsidian 归档的 Markdown。

#### 聊天记录项目化 / [long-chat-task-processor](skills/long-chat-task-processor)

把以 Markdown 标题组织的超长聊天记录转为待办、决策和里程碑文档。它严格基于文档目录结构（TOC）分段处理，确保对话上下文不丢，能自动积累人名和黑话术语。

#### IM 知识库整理 / [im-local-kb](skills/im-local-kb)

IM 知识整理和分析技能，专注于从聊天记录中提取高价值的知识。它维护一个基于 Markdown 的本地文件系统，支持数据摄入、断档诊断和知识生成。

#### 项目交互式学习 / [project-learner](skills/project-learner)

让 Agent 充当导师，在讲解项目代码或底层技术时，自动将过程记录到持久化的学习日志中。支持断点续学，让学习过程像项目开发一样有据可查。

#### 研究报告编写 / [content-research-writer](skills/content-research-writer)

用于撰写深度文章、技术文档或博客时。助手协助梳理大纲、交叉验证资料、管理引用链路，并在保持作者原始语气的基础上优化段落逻辑。与简单生成文本的工具不同，它强调协作式写作，避免“AI腔”泛滥。

#### 笔记库查资料 / [obsidian-knowledge-filter](skills/obsidian-knowledge-filter)

面对庞大 Obsidian 知识库时，通过关键词定位相关笔记，自动提取上下文并综合生成专题报告。支持人工筛选介入，防止误关联。适合周期性复盘、跨笔记主题研究（如「过去半年关于用户关于 LLM 的所有暴论」）。

#### 去模型味儿 / [remove-model-cliche](skills/remove-model-cliche)

识别并替换文本中高频出现的模型化表达（如「不仅…而且…」、「核心价值」等），基于公开语料库提供自然替代表达。适用于需要提升文案真诚度的场景，如内部沟通邮件、个人博客或用户访谈摘要。

#### 写周报 / [weekly-report-writer](skills/weekly-report-writer)

### 二、在线平台 Agent 化

#### 部署到 ModelScope / [deploy-folder-to-modelscope](skills/deploy-folder-to-modelscope)

自动化 ModelScope 仓库发布流程：克隆目标仓库 → 复制指定子目录 → 提交带语义化信息的 commit → 推送远程。支持环境变量配置访问令牌。显著降低从实验到社区共享的摩擦成本。

### 三、项目管理与开发协作范式

定义可重复执行的开发流程与协作规范，提升模型在代码库中开发的效率和长期一致性。

可以按不同项目选择不同的范式。

#### 完整版项目管理范式 / [project-management](skills/project-management)

确立项目级基础规则：Monorepo 目录结构、文档命名规范（`YYYYMMDD-type-topic.md`）、Git 分支策略（feature/hotfix/release）、任务追踪机制（TODO 标签与状态流转），给项目仓库一个限定完全的开发范式。

#### PMP 式迭代流程 / [pmp-dev-process](skills/pmp-dev-process)

引入结构化的迭代流程：修订章程 → 规划确认 → 执行 → 验证。适用于开启新功能、进行重大变更或需要严谨记录的场景。

#### 设计理念整理 / [project-design-concept-organizer](skills/project-design-concept-organizer)

专门用来提炼项目中的隐性知识。把分散的代码变更抽象为设计模式或协议规范，确保项目在复杂化过程中保持设计的一致性。

#### Git 安全回退 / [git-snapshot-rollback](skills/git-snapshot-rollback)

在执行 `git reset --hard` 前自动将当前状态快照到存档分支，并在 `ARCHIVE.md` 中记录双向链接。确保回退操作安全且决策流可追溯。

#### 轻量版项目管理范式 / [doc-todo-log-loop](skills/doc-todo-log-loop)

作为轻量级默认开发循环，适用于无复杂流程的中小型项目。要求每项任务始于文档分析 → 生成 TODO 清单 → 开发后附加执行日志 → 提交前验证闭环。强调人的确认，最小化「想到哪做到哪」的不可控性，也防止自己忘掉。

#### TDD 驱动的工作流 / [tdd-dev-cycle](skills/tdd-dev-cycle)

对代码质量有明确要求的场景启用。强制要求测试先行：输入/输出定义 → 编写测试用例 → 实现逻辑 → 验证覆盖率 → 修复边界条件。该流程虽增加初期成本，但显著减少后期 Debug 时间，尤其适用于复杂 SQL 或算法模块。

#### 基于浏览器的测试 / [browser-testing](skills/browser-testing)

定义了一套不依赖重型框架的 E2E 测试流。测试用例写在 Markdown 里，通过截图和人工比对验证功能，结果存放在应用目录中作为凭证。

### 四、辅助工具

针对特定高频率、低创造性但易出错的机械性任务提供的专用解决方案。

#### 联系人/群组整理 / [im-contact-sorter](skills/im-contact-sorter)

针对缺少分类功能的 IM 软件。通过「截图-OCR-合并-分析」的流水线，识别未分类的项目并生成报告，辅助进行清理和资产归档。

#### 媒体库整理 / [media-organizer](skills/media-organizer)

处理多媒体资产时的命名与分类工具。基于文件元数据（拍摄时间）或图像内容分析，自动生成 `YYYY-MM-DD_项目_描述.png` 格式的文件名，并输出带缩略图的索引 README。适用于设计素材归档、用户反馈截图整理等场景。用于维护运营资产库。

#### 看看剪贴板图片 / [paste-image](skills/paste-image)

打通 macOS 剪贴板与 LLM 分析管道的桥梁。运行后自动将剪贴板中的图片保存为本地 PNG 文件，并返回路径供后续 Skill 调用。适用于「截图给 Coding Agent 看看效果」的场景。

#### 做微信表情包 / [wx-emoji-maker](skills/wx-emoji-maker)

微信表情包批量生成工具。自动添加透明边框、调整至 240×240 像素、生成预览图包。虽属边缘功能，但在团队文化构建（如节日表情、梗图传播）中有不可替代的实用价值。

#### 代码库术语审计 / [code-naming-auditor](skills/code-naming-auditor)

代码库术语一致性检查器。基于项目 Glossary 文件扫描变量/函数名，识别如 `getUserInfo()` 与 `fetchUserDetails()` 的命名冲突，输出重构建议。适合长期维护项目或微服务架构中保持领域语言统一。
