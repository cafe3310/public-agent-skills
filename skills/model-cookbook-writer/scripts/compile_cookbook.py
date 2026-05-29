#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import base64
import json

def log_info(msg):
    print(f"[\033[94mINFO\033[0m] {msg}")

def log_success(msg):
    print(f"[\033[92mSUCCESS\033[0m] {msg}")

def log_error(msg):
    print(f"[\033[91mERROR\033[0m] {msg}")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cookbook 编译预览 - Ring-2.6-1T</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#f5f3ff',
                            100: '#ede9fe',
                            500: '#8b5cf6',
                            600: '#7c3aed',
                            700: '#6d28d9',
                            900: '#4c1d95',
                        }
                    }
                }
            }
        }
    </script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Highlight.js -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github-dark-dimmed.css">
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/languages/python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/languages/json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/languages/markdown.min.js"></script>
    <!-- Marked.js -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0b0f19;
        }
        
        .heading-font {
            font-family: 'Outfit', sans-serif;
        }

        .glass-panel {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .glass-sidebar {
            background: rgba(11, 15, 25, 0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Customize markdown output style */
        .markdown-body {
            color: #d1d5db;
            line-height: 1.75;
        }
        .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        .markdown-body h1 { font-size: 1.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 0.3em; }
        .markdown-body h2 { font-size: 1.5rem; }
        .markdown-body h3 { font-size: 1.25rem; }
        .markdown-body p { margin-bottom: 1.25em; }
        .markdown-body ul, .markdown-body ol { padding-left: 1.5em; margin-bottom: 1.25em; list-style-type: disc; }
        .markdown-body ol { list-style-type: decimal; }
        .markdown-body li { margin-bottom: 0.5em; }
        .markdown-body blockquote {
            border-left: 4px solid #8b5cf6;
            background: rgba(139, 92, 246, 0.1);
            padding: 0.75rem 1.25rem;
            margin: 1.5rem 0;
            border-radius: 0 0.375rem 0.375rem 0;
            color: #e5e7eb;
        }
        .markdown-body code {
            font-family: 'Fira Code', monospace;
            background: rgba(255, 255, 255, 0.08);
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.875em;
            color: #f472b6;
        }
        .markdown-body pre code {
            background: none;
            padding: 0;
            font-size: 0.9em;
            color: inherit;
        }
        .markdown-body pre {
            background: #111827;
            padding: 1.25rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin: 1.5rem 0;
        }
        .markdown-body table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }
        .markdown-body th, .markdown-body td {
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.75rem 1rem;
            text-align: left;
        }
        .markdown-body th {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
            font-weight: 600;
        }
        .markdown-body tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02);
        }

        /* Sidebar table of contents customization */
        #toc-container ul {
            padding-left: 1.25rem;
            list-style-type: none;
        }
        #toc-container > ul {
            padding-left: 0;
        }
        #toc-container li {
            margin: 0.5rem 0;
            position: relative;
        }
        #toc-container a {
            display: inline-block;
            color: #9ca3af;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            text-decoration: none;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        #toc-container a:hover {
            color: #8b5cf6;
            background: rgba(139, 92, 246, 0.1);
        }
        #toc-container .active-toc-link {
            color: #a78bfa !important;
            font-weight: 600;
            background: rgba(139, 92, 246, 0.15);
            box-shadow: inset 0 0 0 1px rgba(139, 92, 246, 0.3);
        }
        
        /* Smooth scrolling custom scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body class="text-gray-300 min-h-screen transition-colors duration-200">
    <!-- Background glows -->
    <div class="fixed top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div class="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-brand-900/10 blur-[150px]"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-900/10 blur-[150px]"></div>
    </div>

    <div class="flex z-10 relative">
        <!-- Sidebar -->
        <aside class="w-80 h-screen sticky top-0 flex flex-col justify-between glass-sidebar z-20 overflow-hidden">
            <div class="p-6 overflow-y-auto flex-1 flex flex-col">
                <div class="flex items-center gap-3 mb-8">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-blue-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
                        <i class="fa-solid fa-book text-white text-lg"></i>
                    </div>
                    <div>
                        <h2 class="text-white heading-font font-bold tracking-tight">Ring-2.6-1T</h2>
                        <p class="text-xs text-brand-500 font-semibold tracking-wider uppercase">Cookbook Preview</p>
                    </div>
                </div>

                <div class="mb-4">
                    <div class="relative">
                        <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-gray-500 text-sm"></i>
                        <input type="text" id="search-box" placeholder="搜索大纲章节..." 
                               class="w-full bg-gray-900/60 border border-gray-800 rounded-lg py-2 pl-9 pr-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-brand-500 transition-colors">
                    </div>
                </div>

                <!-- Outline Tree -->
                <div class="flex-1 overflow-y-auto pr-1" id="toc-container">
                    <!-- Dynamic Menu Tree -->
                </div>
            </div>

            <!-- Footer / Stats -->
            <div class="p-6 bg-gray-900/30 border-t border-gray-800 flex flex-col gap-2">
                <div class="flex justify-between items-center text-xs">
                    <span class="text-gray-500">编译章节：</span>
                    <span class="text-white font-semibold" id="stat-chapters">0</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                    <span class="text-gray-500">微评测项 (Benches)：</span>
                    <span class="text-white font-semibold" id="stat-benches">0</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                    <span class="text-gray-500">占位/未完工章节：</span>
                    <span class="text-rose-500 font-semibold flex items-center gap-1">
                        <i class="fa-solid fa-square-minus text-[10px]"></i>
                        <span id="stat-todo">0</span>
                    </span>
                </div>
                <div class="mt-2 flex justify-between items-center border-t border-gray-800/80 pt-3">
                    <button onclick="toggleTheme()" class="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-2">
                        <i class="fa-solid fa-circle-half-stroke" id="theme-icon"></i>
                        <span class="text-xs">色彩切换</span>
                    </button>
                    <span class="text-[10px] text-gray-600 font-mono" id="compilation-date"></span>
                </div>
            </div>
        </aside>

        <!-- Main Body -->
        <main class="flex-1 min-h-screen px-12 py-10 overflow-x-hidden">
            <header class="mb-10 flex justify-between items-start border-b border-gray-800 pb-6">
                <div>
                    <div class="flex items-center gap-2 text-xs text-brand-500 font-mono tracking-widest uppercase mb-1">
                        <span>Workspace Cookbooks</span>
                        <span>/</span>
                        <span id="cookbook-folder-name">FolderName</span>
                    </div>
                    <h1 class="text-3xl text-white font-extrabold heading-font tracking-tight" id="cookbook-title">加载中...</h1>
                </div>
                <div class="flex gap-3">
                    <button onclick="window.print()" class="px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-all">
                        <i class="fa-solid fa-print"></i> 打印 / 导出 PDF
                    </button>
                </div>
            </header>

            <!-- Container for Markdown Content -->
            <article class="markdown-body max-w-4xl prose prose-invert" id="content-area">
                <!-- Content gets dynamically rendered here -->
                <div class="flex items-center justify-center h-64">
                    <div class="flex flex-col items-center gap-4">
                        <i class="fa-solid fa-circle-notch fa-spin text-brand-500 text-3xl"></i>
                        <span class="text-sm text-gray-500 font-mono">正在渲染编译内容...</span>
                    </div>
                </div>
            </article>
        </main>
    </div>

    <!-- Data Injection -->
    <script>
        // Encoded data injected by compiler
        const b64TocMarkdown = "{{TOC_MARKDOWN_BASE64}}";
        const b64ContentsMarkdown = "{{CONTENTS_MARKDOWN_BASE64}}";
        const metadata = {{METADATA_JSON}};
        
        // Decode base64 to UTF-8 safely supporting emojis and unicode characters
        function decodeBase64Utf8(b64) {
            const binary = atob(b64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {
                bytes[i] = binary.charCodeAt(i);
            }
            return new TextDecoder("utf-8").decode(bytes);
        }

        const tocMarkdown = decodeBase64Utf8(b64TocMarkdown);
        const contentsMarkdown = decodeBase64Utf8(b64ContentsMarkdown);

        // Inject configuration details
        document.getElementById('cookbook-folder-name').textContent = metadata.folder_name;
        document.getElementById('cookbook-title').textContent = metadata.title;
        document.getElementById('compilation-date').textContent = metadata.compiled_at;
        document.getElementById('stat-chapters').textContent = metadata.stat_chapters;
        document.getElementById('stat-benches').textContent = metadata.stat_benches;
        document.getElementById('stat-todo').textContent = metadata.stat_todos;

        // Configure marked options compatibly
        marked.use({
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-',
            gfm: true,
            breaks: true
        });

        // 1. Render TOC
        document.getElementById('toc-container').innerHTML = marked.parse(tocMarkdown);

        // 2. Render Main Body
        document.getElementById('content-area').innerHTML = marked.parse(contentsMarkdown);

        // Adjust link targets in TOC to scroll smoothly to their respective anchors
        const tocLinks = document.querySelectorAll('#toc-container a');
        tocLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = href.substring(1);
                    const targetEl = document.getElementById(targetId);
                    if (targetEl) {
                        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        // Add active class
                        tocLinks.forEach(l => l.classList.remove('active-toc-link'));
                        link.classList.add('active-toc-link');
                    }
                });
            }
        });

        // Highlight active link based on scroll position
        window.addEventListener('scroll', () => {
            let activeId = null;
            const sections = document.querySelectorAll('article div[id^="sec-"]');
            const scrollPos = window.scrollY + 120; // offsets offset height of header
            
            sections.forEach(sec => {
                if (scrollPos >= sec.offsetTop) {
                    activeId = sec.getAttribute('id');
                }
            });

            if (activeId) {
                tocLinks.forEach(link => {
                    if (link.getAttribute('href') === '#' + activeId) {
                        link.classList.add('active-toc-link');
                    } else {
                        link.classList.remove('active-toc-link');
                    }
                });
            }
        });

        // Search Filter
        document.getElementById('search-box').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const listItems = document.querySelectorAll('#toc-container li');
            
            listItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query) || query === '') {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });

        // Theme Toggle (Light/Dark)
        function toggleTheme() {
            const html = document.documentElement;
            const icon = document.getElementById('theme-icon');
            if (html.classList.contains('dark')) {
                html.classList.remove('dark');
                html.classList.add('light');
                document.body.style.backgroundColor = '#f9fafb';
                // Switch highlight theme
                const hlCss = document.querySelector('link[href*="github-dark"]');
                if (hlCss) hlCss.setAttribute('href', 'https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github.css');
            } else {
                html.classList.remove('light');
                html.classList.add('dark');
                document.body.style.backgroundColor = '#0b0f19';
                const hlCss = document.querySelector('link[href*="github.css"]');
                if (hlCss) hlCss.setAttribute('href', 'https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/github-dark-dimmed.css');
            }
        }
    </script>
</body>
</html>
"""

def parse_wikilink(line):
    # Regex to find WikiLinks [[file_path|label]] or [[file_path]]
    match = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', line)
    if match:
        path = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else os.path.basename(path)
        return path, label
    return None

def path_to_anchor_id(filepath):
    # Clean the filepath to generate a valid HTML ID
    clean = re.sub(r'[^a-zA-Z0-9-]', '-', filepath)
    # Deduplicate dashes
    clean = re.sub(r'-+', '-', clean)
    return f"sec-{clean.strip('-')}"

def parse_markdown_to_cells(md_content):
    cells = []
    current_lines = []
    in_code = False
    
    for line in md_content.splitlines():
        # Check for start of python code block
        if line.strip().startswith("```python"):
            if current_lines:
                cells.append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [l + "\n" for l in current_lines]
                })
                current_lines = []
            in_code = True
        # Check for end of code block
        elif line.strip() == "```" and in_code:
            if current_lines:
                cells.append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [l + "\n" for l in current_lines]
                })
                current_lines = []
            in_code = False
        else:
            current_lines.append(line)
            
    # Flush remaining lines
    if current_lines:
        cell_type = "code" if in_code else "markdown"
        cell = {
            "cell_type": cell_type,
            "metadata": {},
            "source": [l + "\n" for l in current_lines]
        }
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        cells.append(cell)
        
    return cells

def compile_cookbook(cookbook_path):
    if not os.path.isdir(cookbook_path):
        log_error(f"指定路径不是有效的目录: {cookbook_path}")
        return False
    
    toc_file = os.path.join(cookbook_path, "toc.md")
    if not os.path.isfile(toc_file):
        log_error(f"在目录中找不到 toc.md: {cookbook_path}")
        return False
    
    log_info(f"读取大纲文件: {toc_file}")
    with open(toc_file, "r", encoding="utf-8") as f:
        toc_lines = f.readlines()
        
    compiled_markdown = []
    preview_toc_lines = []
    
    stat_chapters = 0
    stat_benches = 0
    stat_todos = 0
    
    # Track anchor mappings
    anchors = {}
    
    # We scan toc.md line by line to compile the actual referenced document contents
    for line in toc_lines:
        parsed = parse_wikilink(line)
        if not parsed:
            # Keep structural comments/headings in the preview TOC
            # But replace WikiLink notations if any
            clean_line = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', r'\2', line)
            preview_toc_lines.append(clean_line)
            continue
            
        rel_filepath, label = parsed
        
        # Absolute path of reference file in repo
        # Paths in wiki link are relative to repo root
        abs_filepath = os.path.abspath(os.path.join(os.getcwd(), rel_filepath))
        anchor_id = path_to_anchor_id(rel_filepath)
        
        # Rewrite wiki link to anchor link for HTML Preview
        rewritten_link = f"[{label}](#{anchor_id})"
        new_line = line.replace(f"[[{rel_filepath}|{label}]]", rewritten_link).replace(f"[[{rel_filepath}]]", rewritten_link)
        preview_toc_lines.append(new_line)
        
        # Read the target file content
        file_content = ""
        is_todo = False
        
        # Check if it represents a Todo / Placeholder based on emojis
        if "🟥" in line or "🟥" in label or "🟥" in rel_filepath:
            is_todo = True
            stat_todos += 1
            
        if "benches/" in rel_filepath:
            stat_benches += 1
        elif "cookbook-chapters/" in rel_filepath:
            stat_chapters += 1
            
        if os.path.isfile(abs_filepath):
            with open(abs_filepath, "r", encoding="utf-8") as f_ref:
                file_content = f_ref.read()
                
            # Strip Frontmatter if present
            if file_content.startswith("---"):
                parts = file_content.split("---", 2)
                if len(parts) >= 3:
                    file_content = parts[2].strip()
        else:
            # File not found or placeholder
            file_content = f"> [!WARNING]\\n> 物理文件不存在或未找到: `{rel_filepath}`。此处为编译占位符。\\n"
            
        # Append to our unified compiler contents
        compiled_markdown.append(f'<div id="{anchor_id}"></div>\n\n')
        compiled_markdown.append(f"> 📄 *源物理文档: [{rel_filepath}](file://{abs_filepath})*\n\n")
        compiled_markdown.append(file_content)
        compiled_markdown.append("\n\n---\n\n")
        
    # Build contents.md text
    full_contents_text = "".join(compiled_markdown)
    
    # Ensure build output directory exists
    folder_name = os.path.basename(os.path.normpath(cookbook_path))
    output_dir = os.path.join(os.getcwd(), "build", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Write the unified contents.md back to the build directory
    contents_file = os.path.join(output_dir, "contents.md")
    log_info(f"写入合并正文文档: {contents_file}")
    with open(contents_file, "w", encoding="utf-8") as f_out:
        f_out.write(full_contents_text)
        
    # 2. Build and export HTML Preview page
    import datetime
    compiled_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get metadata
    title_match = re.search(r'# (.*)', "".join(toc_lines))
    cookbook_title = title_match.group(1).strip() if title_match else "Ring-2.6-1T Cookbook"
    
    meta_json = {
        "folder_name": folder_name,
        "title": cookbook_title,
        "compiled_at": compiled_time,
        "stat_chapters": stat_chapters,
        "stat_benches": stat_benches,
        "stat_todos": stat_todos
    }
    
    # Base64 encoding to prevent encoding escaping issues
    toc_b64 = base64.b64encode("".join(preview_toc_lines).encode("utf-8")).decode("utf-8")
    contents_b64 = base64.b64encode(full_contents_text.encode("utf-8")).decode("utf-8")
    
    # Replace templates
    html_output = HTML_TEMPLATE
    html_output = html_output.replace("{{TOC_MARKDOWN_BASE64}}", toc_b64)
    html_output = html_output.replace("{{CONTENTS_MARKDOWN_BASE64}}", contents_b64)
    html_output = html_output.replace("{{METADATA_JSON}}", json.dumps(meta_json))
    
    preview_file = os.path.join(output_dir, "preview.html")
    log_info(f"生成 HTML 预览网页: {preview_file}")
    with open(preview_file, "w", encoding="utf-8") as f_html:
        f_html.write(html_output)
        
    # 3. Build and export Jupyter Notebook (.ipynb)
    log_info("编译并输出 Jupyter Notebook...")
    
    # Prefix introduction details
    intro_md = f"""# {cookbook_title}

> 📄 **交付包名称**: `{folder_name}`
> 📅 **编译时间**: {compiled_time}
> 🛠️ **模型目标**: Ring-2.6-1T
> 📊 **编译指标**:
> - 章节数: {stat_chapters}
> - 评测项 (Benches): {stat_benches}
> - 待完工 TODO 章节数: {stat_todos}

---

## 📖 目录与导航

"""
    intro_md += "".join(preview_toc_lines)
    intro_md += "\n\n---"
    
    notebook_cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [l + "\n" for l in intro_md.splitlines()]
        }
    ]
    
    # Parse compiled content into cells
    notebook_cells.extend(parse_markdown_to_cells(full_contents_text))
    
    notebook_data = {
        "cells": notebook_cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    notebook_file = os.path.join(output_dir, "preview.ipynb")
    log_info(f"生成 Jupyter Notebook: {notebook_file}")
    with open(notebook_file, "w", encoding="utf-8") as f_nb:
        json.dump(notebook_data, f_nb, indent=2, ensure_ascii=False)
        
    log_success(f"============================================================")
    log_success(f"Cookbook 编译成功!")
    log_success(f"输出目录: {output_dir}")
    log_success(f"编译正文: {contents_file}")
    log_success(f"预览网页: {preview_file}")
    log_success(f"预览 Notebook: {notebook_file}")
    log_success(f"可直接双击 HTML 网页预览，或在 Jupyter / VS Code 中打开 .ipynb 运行代码:")
    log_success(f"file://{os.path.abspath(preview_file)}")
    log_success(f"============================================================")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Scan cookbooks folder
        cookbooks_dir = os.path.abspath(os.path.join(os.getcwd(), "cookbooks"))
        if os.path.isdir(cookbooks_dir):
            subdirs = [os.path.join(cookbooks_dir, d) for d in os.listdir(cookbooks_dir) if os.path.isdir(os.path.join(cookbooks_dir, d))]
            if len(subdirs) == 1:
                compile_cookbook(subdirs[0])
            elif len(subdirs) > 1:
                log_info("在 cookbooks/ 下检测到多个目录，请指定一个要编译的目录:")
                for sd in subdirs:
                    print(f"  - python3 scripts/compile_cookbook.py cookbooks/{os.path.basename(sd)}")
            else:
                log_error("在 cookbooks/ 目录下未检测到任何 Cookbook 交付项目。")
        else:
            log_error("请提供要编译的 Cookbook 路径，例如: python3 scripts/compile_cookbook.py cookbooks/2026-05-29_🟥_ring-2.6-1t_prompt-guide-and-recipes")
    else:
        compile_cookbook(sys.argv[1])
