---
name: agent-browser
description: 为 Agent 设计的自动化浏览器 CLI 工具，也能操作 Electron 桌面应用。当需要与网站交互（包括页面导航）时使用
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*)
author: https://github.com/vercel-labs/agent-browser
depends_on_skill: []
depends_on_binary:
  - node
---

# agent-browser

Fast browser automation CLI for AI agents. Chrome/Chromium via CDP with
accessibility-tree snapshots and compact `@eN` element refs.

## Start here

This file is a discovery stub, not the usage guide. Before running any
`agent-browser` command, load the actual workflow content from the CLI:

```bash
agent-browser skills get core             # start here — workflows, common patterns, troubleshooting
agent-browser skills get core --full      # include full command reference and templates
```

The CLI serves skill content that always matches the installed version,
so instructions never go stale. The content in this stub cannot change
between releases, which is why it just points at `skills get core`.

## Specialized skills

Load a specialized skill when the task falls outside browser web pages:

```bash
agent-browser skills get electron          # Electron desktop apps (VS Code, Slack, Discord, Figma, ...)
agent-browser skills get slack             # Slack workspace automation
agent-browser skills get dogfood           # Exploratory testing / QA / bug hunts
agent-browser skills get vercel-sandbox    # agent-browser inside Vercel Sandbox microVMs
agent-browser skills get agentcore         # AWS Bedrock AgentCore cloud browsers
```

Run `agent-browser skills list` to see everything available on the
installed version.

## Why agent-browser

- Fast native Rust CLI, not a Node.js wrapper
- Works with any AI agent (Cursor, Claude Code, Codex, Continue, Windsurf, etc.)
- Chrome/Chromium via CDP with no Playwright or Puppeteer dependency
- Accessibility-tree snapshots with element refs for reliable interaction
- Sessions, authentication vault, state persistence, video recording
- Specialized skills for Electron apps, Slack, exploratory testing, cloud providers
