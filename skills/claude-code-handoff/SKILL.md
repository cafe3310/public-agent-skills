---
name: claude-code-handoff
description: 从 Claude Code 的 Session 解析 jsonl 对话记录，接续执行任务
argument-hint: "Claude Code 的 session ID（如 UUID），或具体的 session.jsonl 文件路径 (必填)"
license: Apache-2.0
author: github/cafe3310
depends_on_skill: []
depends_on_binary:
  - python3
---

# claude-code-handoff

解析本地 Claude Code 的 session jsonl 结构，诊断中断原因，自动恢复上下文或交接文档并指导接续任务。

## 适用场景
1. **任务接力**：开发工作由 Claude Code CLI 启动并开发至一半，现在需要由 Gemini (Antigravity 平台) 接管。
2. **死锁/限制中断恢复**：Claude Code 在运行过程中遇到了 API 频率超限 (429 Rate Limit) 或上下文超长窗口超限 (422 Context Window Exceeded) 等错误强制中止，需要无缝迁移至 Gemini 续作。
3. **状态诊断**：快速查看本地最新的 Claude Code session，查看最后执行的对话历史、调用的工具以及运行时的 git 分支和 cwd 信息。

## 工作原理
1. **定位 Session 文件**：
   根据传入的 `session ID`（如 UUID）或 `session 文件名`，在 Claude 目录（包括官方的 `~/.claude/projects/`）中自动搜索对应的 `.jsonl` 文件。同时也支持传入具体的本地文件路径。
2. **提取历史与状态**：
   - 提取 session 中最近几轮的对话历史；
   - 从 `attachment` 事件中提取最后生成的 `HANDOFF.md` ；
   - 分析最近的 `system` 和 `assistant` 事件是否有报错。
3. **输出 Handoff 并落盘**：
   - 自动在项目根目录生成/更新 `HANDOFF.md`。如果 session 包含已加载的 `HANDOFF.md` 附件，则以它为准；否则根据最近的上下文合成一份草拟版本。
   - 生成一段指令用于用户直接复制粘贴给接续的 Agent 引导后续工作。

## 使用步骤
1. 用户在对话中调用此技能，传入特定的 session ID 或 jsonl 文件路径。
2. Agent 执行解析脚本：
   ```bash
   python3 {path_to_public-agent-skills}/skills/claude-code-handoff/scripts/claude_handoff_parser.py -f <session_id_or_file_path> [-o /path/to/HANDOFF.md]
   ```
3. 根据输出中的提示复制接力指令，并加载更新后的 `HANDOFF.md` 继续工作。
