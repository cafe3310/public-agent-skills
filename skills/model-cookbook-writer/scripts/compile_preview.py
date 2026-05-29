#!/usr/bin/env python3
"""Compile cookbook-chapters and cookbooks into a minimal light-themed preview HTML.

All chapter content (content.md, benchmarks.md, examples.md) is embedded inline
so the output is a single self-contained HTML file that works offline.
"""

import os
import re
import json
import base64
import datetime
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(REPO_ROOT, "cookbook-chapters")
COOKBOOKS_DIR = os.path.join(REPO_ROOT, "cookbooks")
BUILD_DIR = os.path.join(REPO_ROOT, "build")


def strip_frontmatter(text):
    """Remove YAML frontmatter from markdown text."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


def read_md_file(filepath):
    """Read a markdown file, strip frontmatter, return content or None."""
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return strip_frontmatter(text)


def get_title_from_content_md(filepath):
    """Extract the first heading from a content.md file."""
    if not os.path.isfile(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                title = re.sub(r'^#+\s*', '', line)
                title = title.replace("✏️🟥 ", "").replace("✏️🟥", "")
                return title
    return None


def has_placeholder_marker(dirpath):
    """Check if a directory or its content.md has 🟥 marker."""
    content_path = os.path.join(dirpath, "content.md")
    if "🟥" in os.path.basename(dirpath):
        return True
    if os.path.isfile(content_path):
        with open(content_path, "r", encoding="utf-8") as f:
            first_lines = f.read(200)
            return "🟥" in first_lines
    return True


# Global contents map: rel_path -> {content, benchmarks, examples}
contents_map = {}


def scan_chapter_tree(base_dir):
    """Recursively scan a chapter directory into a tree structure."""
    nodes = []
    if not os.path.isdir(base_dir):
        return nodes

    entries = sorted(os.listdir(base_dir))
    for entry in entries:
        full_path = os.path.join(base_dir, entry)
        if not os.path.isdir(full_path):
            continue
        if entry.startswith(".") or entry == "EXAMPLE-tool-calling":
            continue

        content_md = os.path.join(full_path, "content.md")
        title = get_title_from_content_md(content_md)
        if title is None:
            title = entry.replace("-", " ").title()

        is_placeholder = has_placeholder_marker(full_path)
        rel_path = os.path.relpath(full_path, REPO_ROOT)

        has_benchmarks = os.path.isfile(os.path.join(full_path, "benchmarks.md"))
        has_examples = os.path.isfile(os.path.join(full_path, "examples.md"))

        # Collect content into the global map
        content_text = read_md_file(content_md)
        bench_text = read_md_file(os.path.join(full_path, "benchmarks.md"))
        examples_text = read_md_file(os.path.join(full_path, "examples.md"))

        if content_text or bench_text or examples_text:
            contents_map[rel_path] = {}
            if content_text:
                contents_map[rel_path]["content"] = content_text
            if bench_text:
                contents_map[rel_path]["benchmarks"] = bench_text
            if examples_text:
                contents_map[rel_path]["examples"] = examples_text

        children = scan_chapter_tree(full_path)

        nodes.append({
            "id": rel_path,
            "title": title,
            "dir_name": entry,
            "placeholder": is_placeholder,
            "has_benchmarks": has_benchmarks,
            "has_examples": has_examples,
            "children": children,
        })

    return nodes


def parse_toc_md(toc_path):
    """Parse a toc.md and extract outline items with indentation."""
    if not os.path.isfile(toc_path):
        return []

    items = []
    with open(toc_path, "r", encoding="utf-8") as f:
        for line in f:
            wikilink = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', line)
            if not wikilink:
                continue

            path = wikilink.group(1).strip()
            label = wikilink.group(2).strip() if wikilink.group(2) else os.path.basename(path)

            indent = len(line) - len(line.lstrip())
            level = indent // 2

            is_bench = "benches/" in path
            is_result = "bench-results/" in path
            is_placeholder = "🟥" in line

            # Read the referenced file into contents_map
            abs_path = os.path.join(REPO_ROOT, path)
            if os.path.isfile(abs_path) and path not in contents_map:
                text = read_md_file(abs_path)
                if text:
                    contents_map[path] = {"content": text}

            items.append({
                "path": path,
                "label": label,
                "level": level,
                "is_bench": is_bench,
                "is_result": is_result,
                "placeholder": is_placeholder,
            })

    return items


def build_catalog():
    """Build the full catalog data structure."""
    catalog = {"tabs": [], "compiled_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

    # Tab 1: Prompting Guide
    pg_dir = os.path.join(CHAPTERS_DIR, "02-prompting-guide")
    if os.path.isdir(pg_dir):
        tree = scan_chapter_tree(pg_dir)
        catalog["tabs"].append({
            "id": "prompting-guide",
            "label": "Prompting Guide",
            "priority": 1,
            "type": "chapter-tree",
            "tree": tree,
        })

    # Tab 2: 主题 Cookbook (methodology + multimodal)
    method_dir = os.path.join(CHAPTERS_DIR, "04-methodology-cookbooks")
    multi_dir = os.path.join(CHAPTERS_DIR, "06-multimodal")
    topic_tree = []
    if os.path.isdir(method_dir):
        topic_tree.extend(scan_chapter_tree(method_dir))
    if os.path.isdir(multi_dir):
        topic_tree.extend(scan_chapter_tree(multi_dir))
    if topic_tree:
        catalog["tabs"].append({
            "id": "topic-cookbooks",
            "label": "主题 Cookbook",
            "priority": 2,
            "type": "chapter-tree",
            "tree": topic_tree,
        })

    # Tab 3: 特定任务 Cookbook
    task_dir = os.path.join(CHAPTERS_DIR, "05-task-recipes")
    if os.path.isdir(task_dir):
        tree = scan_chapter_tree(task_dir)
        catalog["tabs"].append({
            "id": "task-recipes",
            "label": "特定任务",
            "priority": 3,
            "type": "chapter-tree",
            "tree": tree,
        })

    # Tab 4+: Each cookbook delivery project
    if os.path.isdir(COOKBOOKS_DIR):
        for entry in sorted(os.listdir(COOKBOOKS_DIR)):
            full = os.path.join(COOKBOOKS_DIR, entry)
            if not os.path.isdir(full):
                continue
            if entry == "EXAMPLE":
                continue
            toc_path = os.path.join(full, "toc.md")
            toc_items = parse_toc_md(toc_path)

            display_name = entry
            display_name = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', display_name)
            display_name = display_name.replace("🟥_", "").replace("_", " ")

            catalog["tabs"].append({
                "id": f"cookbook-{entry}",
                "label": display_name,
                "priority": 10,
                "type": "toc-outline",
                "toc_items": toc_items,
            })

    return catalog


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cookbook Preview</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github.min.css">
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/json.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/yaml.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/bash.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/javascript.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/xml.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --sidebar-w: 300px;
  --border: #e5e7eb;
  --bg: #ffffff;
  --bg-subtle: #f9fafb;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --accent: #2563eb;
  --accent-bg: #eff6ff;
  --placeholder: #f59e0b;
  --placeholder-bg: #fffbeb;
  --bench: #8b5cf6;
  --result: #10b981;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif;
  color: var(--text);
  background: var(--bg);
  height: 100vh;
  overflow: hidden;
}

.layout {
  display: flex;
  height: 100vh;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-w);
  min-width: var(--sidebar-w);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  background: var(--bg);
  overflow: hidden;
}

.sidebar-tabs {
  padding: 12px 12px 0;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tab-btn {
  padding: 5px 9px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid var(--border);
  border-radius: 5px;
  background: var(--bg);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 8px;
}

.tab-btn:hover {
  background: var(--bg-subtle);
  color: var(--text);
}

.tab-btn.active {
  background: var(--accent-bg);
  border-color: var(--accent);
  color: var(--accent);
}

.sidebar-outline {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.sidebar-outline::-webkit-scrollbar { width: 4px; }
.sidebar-outline::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px; }

/* Tree items */
.tree-node {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tree-item {
  display: flex;
  align-items: flex-start;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12.5px;
  line-height: 1.4;
  color: var(--text);
  transition: background 0.1s;
  gap: 6px;
}

.tree-item:hover {
  background: var(--bg-subtle);
}

.tree-item.active {
  background: var(--accent-bg);
  color: var(--accent);
}

.tree-item.placeholder {
  color: var(--text-muted);
}

.tree-item .marker {
  flex-shrink: 0;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: 6px;
}

.tree-item.placeholder .marker {
  background: var(--placeholder);
}

.tree-item.active .marker {
  background: var(--accent);
}

.tree-item .label {
  flex: 1;
  word-break: break-word;
}

.tree-item .badges {
  display: flex;
  gap: 3px;
  flex-shrink: 0;
  margin-top: 2px;
}

.badge {
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.badge-bench {
  background: #f3f0ff;
  color: var(--bench);
}

.badge-example {
  background: #ecfdf5;
  color: var(--result);
}

.tree-children {
  margin-left: 14px;
  list-style: none;
  padding: 0;
}

/* TOC outline items */
.toc-item {
  display: flex;
  align-items: flex-start;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12.5px;
  line-height: 1.4;
  color: var(--text);
  gap: 6px;
  cursor: pointer;
  transition: background 0.1s;
}

.toc-item:hover {
  background: var(--bg-subtle);
}

.toc-item.active {
  background: var(--accent-bg);
  color: var(--accent);
}

.toc-item.is-bench {
  color: var(--bench);
  font-size: 11.5px;
}

.toc-item.is-result {
  color: var(--result);
  font-size: 11.5px;
}

.toc-item.placeholder {
  color: var(--text-muted);
}

.toc-item .toc-marker {
  flex-shrink: 0;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: 6px;
}

.toc-item.placeholder .toc-marker { background: var(--placeholder); }
.toc-item.is-bench .toc-marker { background: var(--bench); }
.toc-item.is-result .toc-marker { background: var(--result); }

/* Main content area */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg);
  overflow: hidden;
}

.content-header {
  padding: 12px 32px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
}

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
}

.breadcrumb span {
  color: var(--text-secondary);
}

.content-tabs {
  display: flex;
  gap: 2px;
  margin-left: auto;
}

.content-tab-btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s;
}

.content-tab-btn:hover {
  color: var(--text-secondary);
  background: var(--bg-subtle);
}

.content-tab-btn.active {
  background: var(--accent-bg);
  border-color: var(--accent);
  color: var(--accent);
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px 48px;
}

.content-body::-webkit-scrollbar { width: 6px; }
.content-body::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  font-size: 14px;
  gap: 8px;
}

.empty-state .empty-icon {
  font-size: 32px;
  opacity: 0.4;
}

/* Markdown rendered content */
.md-body {
  max-width: 720px;
  line-height: 1.7;
  font-size: 14.5px;
  color: var(--text);
}

.md-body h1 { font-size: 1.6em; font-weight: 700; margin: 1.4em 0 0.5em; padding-bottom: 0.3em; border-bottom: 1px solid var(--border); }
.md-body h2 { font-size: 1.35em; font-weight: 600; margin: 1.3em 0 0.4em; }
.md-body h3 { font-size: 1.15em; font-weight: 600; margin: 1.2em 0 0.3em; }
.md-body h4 { font-size: 1em; font-weight: 600; margin: 1em 0 0.3em; }
.md-body p { margin: 0.8em 0; }
.md-body ul, .md-body ol { padding-left: 1.5em; margin: 0.8em 0; }
.md-body li { margin: 0.3em 0; }
.md-body blockquote {
  border-left: 3px solid var(--accent);
  padding: 0.5em 1em;
  margin: 1em 0;
  background: var(--bg-subtle);
  color: var(--text-secondary);
  border-radius: 0 4px 4px 0;
}
.md-body code {
  font-family: "SF Mono", "Fira Code", "JetBrains Mono", monospace;
  background: #f3f4f6;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.88em;
}
.md-body pre {
  background: #f8f9fa;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 16px;
  overflow-x: auto;
  margin: 1em 0;
}
.md-body pre code {
  background: none;
  padding: 0;
  font-size: 0.85em;
  line-height: 1.5;
}
.md-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 0.9em;
}
.md-body th, .md-body td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}
.md-body th {
  background: var(--bg-subtle);
  font-weight: 600;
}
.md-body hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2em 0;
}
.md-body a {
  color: var(--accent);
  text-decoration: none;
}
.md-body a:hover {
  text-decoration: underline;
}
.md-body strong { font-weight: 600; }

/* Footer */
.sidebar-footer {
  padding: 8px 12px;
  border-top: 1px solid var(--border);
  font-size: 10px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
}
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-tabs" id="tabs-container"></div>
    <div class="sidebar-outline" id="outline-container"></div>
    <div class="sidebar-footer">
      <span id="stats"></span>
      <span id="compiled-at"></span>
    </div>
  </aside>
  <main class="main-content" id="main-content">
    <div class="content-header" id="content-header" style="display:none">
      <div class="breadcrumb" id="breadcrumb"></div>
      <div class="content-tabs" id="content-tabs"></div>
    </div>
    <div class="content-body" id="content-body">
      <div class="empty-state">
        <div class="empty-icon">&#9776;</div>
        <div>选择左侧章节查看内容</div>
      </div>
    </div>
  </main>
</div>

<script>
// Decode embedded contents
const CONTENTS_B64 = "__CONTENTS_BASE64__";
const CONTENTS = JSON.parse(
  new TextDecoder().decode(
    Uint8Array.from(atob(CONTENTS_B64), c => c.charCodeAt(0))
  )
);

const CATALOG = __CATALOG_JSON__;

// Configure marked
marked.use({
  gfm: true,
  breaks: false,
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return code;
  }
});

let activeTab = CATALOG.tabs[0]?.id || null;
let activePath = null;
let activeSubTab = 'content';

function renderTabs() {
  const container = document.getElementById('tabs-container');
  container.innerHTML = CATALOG.tabs.map(tab =>
    `<button class="tab-btn ${tab.id === activeTab ? 'active' : ''}" data-id="${tab.id}">${tab.label}</button>`
  ).join('');

  container.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeTab = btn.dataset.id;
      renderTabs();
      renderOutline();
    });
  });
}

function renderTreeNode(node) {
  const placeholderCls = node.placeholder ? ' placeholder' : '';
  const activeCls = node.id === activePath ? ' active' : '';
  let badges = '';
  if (node.has_benchmarks) badges += '<span class="badge badge-bench">B</span>';
  if (node.has_examples) badges += '<span class="badge badge-example">E</span>';

  let childrenHtml = '';
  if (node.children && node.children.length > 0) {
    childrenHtml = '<ul class="tree-children">' +
      node.children.map(c => `<li>${renderTreeNode(c)}</li>`).join('') +
      '</ul>';
  }

  return `<div class="tree-item${placeholderCls}${activeCls}" data-path="${node.id}">
    <span class="marker"></span>
    <span class="label">${node.title}</span>
    ${badges ? `<span class="badges">${badges}</span>` : ''}
  </div>${childrenHtml}`;
}

function renderTocItem(item) {
  let cls = 'toc-item';
  if (item.is_bench) cls += ' is-bench';
  else if (item.is_result) cls += ' is-result';
  if (item.placeholder) cls += ' placeholder';
  if (item.path === activePath) cls += ' active';

  const indent = item.level * 14;
  return `<div class="${cls}" style="padding-left: ${8 + indent}px" data-path="${item.path}">
    <span class="toc-marker"></span>
    <span class="label">${item.label}</span>
  </div>`;
}

function renderOutline() {
  const container = document.getElementById('outline-container');
  const tab = CATALOG.tabs.find(t => t.id === activeTab);
  if (!tab) {
    container.innerHTML = '<div style="padding:20px;color:var(--text-muted)">无内容</div>';
    return;
  }

  if (tab.type === 'chapter-tree') {
    container.innerHTML = '<ul class="tree-node">' +
      tab.tree.map(n => `<li>${renderTreeNode(n)}</li>`).join('') +
      '</ul>';
  } else if (tab.type === 'toc-outline') {
    container.innerHTML = tab.toc_items.map(item => renderTocItem(item)).join('');
  }

  // Bind click events
  container.querySelectorAll('[data-path]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      const path = el.dataset.path;
      selectItem(path);
    });
  });

  // Stats
  const stats = document.getElementById('stats');
  if (tab.type === 'chapter-tree') {
    const count = countNodes(tab.tree);
    stats.textContent = `${count.total} 章节 · ${count.placeholder} 待完成`;
  } else {
    const total = tab.toc_items.length;
    const placeholders = tab.toc_items.filter(i => i.placeholder).length;
    stats.textContent = `${total} 条目 · ${placeholders} 占位`;
  }
}

function selectItem(path) {
  activePath = path;
  activeSubTab = 'content';
  renderOutline();
  renderContent();
}

function renderContent() {
  const header = document.getElementById('content-header');
  const body = document.getElementById('content-body');
  const breadcrumb = document.getElementById('breadcrumb');
  const contentTabs = document.getElementById('content-tabs');

  if (!activePath) {
    header.style.display = 'none';
    body.innerHTML = '<div class="empty-state"><div class="empty-icon">&#9776;</div><div>选择左侧章节查看内容</div></div>';
    return;
  }

  header.style.display = 'flex';

  // Breadcrumb
  const parts = activePath.replace('cookbook-chapters/', '').split('/');
  breadcrumb.innerHTML = parts.map((p, i) =>
    i === parts.length - 1 ? `<span>${p}</span>` : p
  ).join(' / ');

  // Find content entry
  const entry = CONTENTS[activePath];

  if (!entry) {
    contentTabs.innerHTML = '';
    body.innerHTML = '<div class="empty-state"><div class="empty-icon">&#9744;</div><div>该章节暂无内容</div><div style="font-size:12px;margin-top:4px">标记为占位 (🟥)，等待编写</div></div>';
    return;
  }

  // Sub-tabs
  const availableTabs = [];
  if (entry.content) availableTabs.push({key: 'content', label: '正文'});
  if (entry.benchmarks) availableTabs.push({key: 'benchmarks', label: 'Benchmarks'});
  if (entry.examples) availableTabs.push({key: 'examples', label: 'Examples'});

  if (!entry[activeSubTab] && availableTabs.length > 0) {
    activeSubTab = availableTabs[0].key;
  }

  if (availableTabs.length > 1) {
    contentTabs.innerHTML = availableTabs.map(t =>
      `<button class="content-tab-btn ${t.key === activeSubTab ? 'active' : ''}" data-subtab="${t.key}">${t.label}</button>`
    ).join('');
    contentTabs.querySelectorAll('.content-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        activeSubTab = btn.dataset.subtab;
        renderContent();
      });
    });
  } else {
    contentTabs.innerHTML = '';
  }

  // Render markdown
  const md = entry[activeSubTab] || '';
  if (!md.trim()) {
    body.innerHTML = '<div class="empty-state"><div class="empty-icon">&#9744;</div><div>该章节暂无内容</div></div>';
    return;
  }

  body.innerHTML = '<div class="md-body">' + marked.parse(md) + '</div>';
  body.scrollTop = 0;

  // Post-process: highlight code blocks
  body.querySelectorAll('pre code').forEach(block => {
    hljs.highlightElement(block);
  });
}

function countNodes(nodes) {
  let total = 0, placeholder = 0;
  for (const n of nodes) {
    total++;
    if (n.placeholder) placeholder++;
    if (n.children) {
      const sub = countNodes(n.children);
      total += sub.total;
      placeholder += sub.placeholder;
    }
  }
  return { total, placeholder };
}

// Init
renderTabs();
renderOutline();
document.getElementById('compiled-at').textContent = CATALOG.compiled_at;
</script>
</body>
</html>
"""


def main():
    global contents_map
    contents_map = {}

    catalog = build_catalog()
    catalog_json = json.dumps(catalog, ensure_ascii=False)

    # Encode contents_map as base64 JSON
    contents_json = json.dumps(contents_map, ensure_ascii=False)
    contents_b64 = base64.b64encode(contents_json.encode("utf-8")).decode("ascii")

    html = HTML_TEMPLATE.replace("__CATALOG_JSON__", catalog_json)
    html = html.replace("__CONTENTS_BASE64__", contents_b64)

    os.makedirs(BUILD_DIR, exist_ok=True)
    output_path = os.path.join(BUILD_DIR, "preview.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    total_chapters = len([k for k in contents_map if "cookbook-chapters/" in k])
    total_size_kb = len(contents_json) / 1024
    print(f"[OK] 预览页面已生成: {output_path}")
    print(f"     内嵌 {len(contents_map)} 个文档 ({total_size_kb:.0f} KB)")
    print(f"     file://{output_path}")


if __name__ == "__main__":
    main()
