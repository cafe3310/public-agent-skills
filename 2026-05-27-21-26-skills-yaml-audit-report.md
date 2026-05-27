# YAML Frontmatter 审计与批量更新方案报告

## 背景与问题说明

- **背景**：用户在 `public-agent-skills` 项目规范（记录于 `AGENTS.md`）中引入了自定义的 YAML frontmatter 属性，包含 `author`、`depends_on_skill` 和 `depends_on_binary`，且 `depends_on_skill` 必须符合 `github/user/repo -> skill_name` 的规范。
- **提出的问题**：
  1. 当前仓库中所有其他技能（共 38 个）的 `SKILL.md` 的 Frontmatter 是否符合新的自定义属性规范。
  2. 每一个技能正确的 `author`、它所依赖的其他技能和系统级二进制程序是什么。
  3. 如何安全、无误、低上下文开销地批量更新这些文件。
- **为什么需要这份文档**：本分析报告汇总了只读审计 subagent 返回的 38 个技能的 Frontmatter 现状和推荐更改内容，作为后续批量安全写入的事实依据和实施方案。

---

## 关联来源文档

- 仓库规范：[AGENTS.md](file:///Users/sipan/workspace/_working/public-agent-skills/AGENTS.md)
- 子任务 3 中处理的技能头部：[interview-processor SKILL.md](file:///Users/sipan/workspace/_working/public-agent-skills/skills/interview-processor/SKILL.md)

---

## 1. 技能依赖与 Frontmatter 审计汇总表

| 目录名 | 技能名 (name) | 当前 author | 推荐 author | 推荐 depends_on_skill | 推荐 depends_on_binary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `agent-browser` | `agent-browser` | `https://github.com/vercel-labs/agent-browser` | `https://github.com/vercel-labs/agent-browser` | `[]` | `[node]` |
| `cafe3310-obsidian-writer` | `cafe3310-obsidian-writer` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `cafe3310-skill-installer` | `cafe3310-skill-installer` | `github/cafe3310` | `github/cafe3310` | `[]` | `[bash]` |
| `code-naming-auditor` | `code-naming-auditor` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `content-tone-adjuster` | `content-tone-adjuster` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `deep-research` | `deep-research` | `cafe3310` | `github/cafe3310` | `- github/vercel-labs/agent-browser -> agent-browser` | `[python3]` |
| `deep-research-partnership-planner` | `deep-research-partnership-planner` | `github/cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-use-claude-plugin -> plugin-search-and-use` | `[]` |
| `deploy-folder-to-modelscope` | `deploy-folder-to-modelscope` | `github/cafe3310` | `github/cafe3310` | `[]` | `[git, python3]` |
| `doc-template-provider` | `doc-template-provider` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `doc-todo-log-loop` | `doc-todo-log-loop` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `gemini-omni-video-to-sticker-gif` | `gemini-omni-video-to-sticker-gif` | `antigravity` | `github/antigravity` | `[]` | `[ffmpeg, ffprobe, python3]` |
| `git-snapshot-rollback` | `git-snapshot-rollback` | `github/cafe3310` | `github/cafe3310` | `[]` | `[git, python3]` |
| `hugging-face-stat` | `hugging-face-stat` | `github/cafe3310` | `github/cafe3310` | `[]` | `[curl, python3]` |
| `im-contact-sorter` | `im-contact-sorter` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `im-local-kb` | `im-local-kb` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `im-wiki-extractor` | `im-wiki-extractor` | `github/cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-memories-off -> memories-off` | `[python3]` |
| `impeccable` | `impeccable` | `https://github.com/pbakaus/impeccable` | `https://github.com/pbakaus/impeccable` | `[]` | `[node]` |
| `learning-assistant` | `learning-assistant` | `cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-memories-off -> memories-off` | `[python3]` |
| `long-audio-to-obsidian` | `long-audio-to-obsidian` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `long-audio-transcript-processor` | `long-audio-transcript-processor` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3, sed]` |
| `long-chat-task-processor` | `long-chat-task-processor` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `media-organizer` | `media-organizer` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `obsidian-knowledge-filter` | `obsidian-knowledge-filter` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `obsidian-todo-collector` | `obsidian-todo-collector` | `github/cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `oneshot-website` | `oneshot-website` | `github/jpcaparas` | `github/jpcaparas` | `[]` | `[python3]` |
| `online-content-collector` | `online-content-collector` | `cafe3310` | `github/cafe3310` | `[]` | `[yt-dlp, pandoc, ffmpeg, python3]` |
| `project-design-concept-organizer`| `project-design-concept-organizer`| `github/cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-doc-todo-log-loop -> doc-todo-log-loop`| `[]` |
| `project-learner` | `project-learner` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `release-showcase-manager` | `release-showcase-manager` | `cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-doc-todo-log-loop -> doc-todo-log-loop`<br>- `github/cafe3310/agent-skill-showcase-video-processor -> showcase-video-processor`<br>- `github/jpcaparas/oneshot-website -> oneshot-website` | `[]` |
| `showcase-video-processor` | `showcase-video-processor` | `github/cafe3310` | `github/cafe3310` | `[]` | `[ffmpeg]` |
| `skill-creator` | `skill-creator` | `github/claude` | `github/claude` | `[]` | `[python3]` |
| `subject-learning-assistant` | `subject-learning-assistant` | `cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-memories-off -> memories-off` | `[python3]` |
| `tech-to-marketing-brief` | `tech-to-marketing-brief` | `github/cafe3310` | `github/cafe3310` | `- github/cafe3310/agent-skill-use-claude-plugin -> plugin-search-and-use` | `[]` |
| `text-watermark-fountain` | `text-watermark-fountain` | `cafe3310` | `github/cafe3310` | `[]` | `[python3]` |
| `twitter-watch` | `twitter-watch` | `cafe3310` | `github/cafe3310` | `- github/vercel-labs/agent-browser -> agent-browser` | `[python3, node, npm]` |
| `use-claude-plugin` | `plugin-search-and-use` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `weekly-report-writer` | `weekly-report-writer` | `github/cafe3310` | `github/cafe3310` | `[]` | `[]` |
| `wx-emoji-maker` | `wx-emoji-maker` | `github/cafe3310` | `github/cafe3310` | `[]` | `[imagemagick, bash]` |

---

## 2. 批量处理与执行方案

由于涉及修改 38 个文件，为了避免主代理产生庞大的上下文开销并提高修改效率，提出两种执行方案：

- **方案 A (Python 自动化脚本 - 推荐)**：
  在 `scratch/` 目录下编写一个 Python 自动化修改脚本。该脚本接收上述表格数据作为配置，批量解析每个 `SKILL.md` 文件的 yaml frontmatter 区域，以手术式的非破坏性方式，精确替换 `author` 并添加 `depends_on_skill` 和 `depends_on_binary`，而保留正文的所有内容。
- **方案 B (分发给 write 权限子代理)**：
  调用一个具备 write 权限的 subagent，由它以分步形式或以脚本形式直接修改这 38 个文件。

**推荐使用方案 A**，我们可以直接在主代理的 terminal 中执行该自动化脚本，也可以将其交给 subagent 执行，能确保操作的确定性。
