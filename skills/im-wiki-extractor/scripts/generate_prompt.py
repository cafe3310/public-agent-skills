import os
import sys
import subprocess

def get_memocli_help(cmd):
    """
    运行 memocli <cmd> --help 并返回输出结果。
    """
    try:
        result = subprocess.run(['memocli', cmd, '--help'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        return f"无法获取 memocli {cmd} 的帮助信息: {str(e)}"

def get_memocli_tools_help(chunk_id):
    """
    返回子代理执行提取任务所需的各个 memocli 工具的权威说明。
    """
    return {
        "help_search": f"```\n{get_memocli_help('search')}\n```\n**按需使用**：仅在非常必要（如报错）时使用。禁止对每个显而易见的成员名字进行重复搜索。",
        "help_create": f"```\n{get_memocli_help('create-entity')}\n```\n用于创建新实体。支持通过多次调用 `--add-rel-out` 和 `--add-rel-in` 一并建立复杂的多重关联。",
        "help_append": f"```\n{get_memocli_help('append-update')}\n```\n用于向已有实体追加信息。支持通过多次调用 `--add-rel-out` 和 `--add-rel-in` 在追加内容的同时建立/更新多重关联。",
        "help_relations": f"```\n{get_memocli_help('manage-relations')}\n```\n用于管理关系。支持通过多次调用 `--add-rel-out`、`--add-rel-in` 或 `--remove-rel-out` 来实现精准的关系调整。",
        "help_merge": f"```\n{get_memocli_help('merge-entities')}\n```\n仅在发现明确的重复项时使用。",
        "global_rules": """
**效率与安全规则：**
- **组合指令优先**：优先使用 `append-update` 或 `create-entity` 的关系参数来合并操作，支持单行指令中多次使用同一个参数名。
- **路径简化**：如果在知识库根目录运行，可以省略 `--path` 参数。
- **原子化操作**：所有的追加操作必须包含来源溯源（文件名:行号）。
- **错误处理**：若遇到逻辑冲突或无法解决的工具报错，立即返回 "ERROR: [原因]"。
"""
    }

def get_lines(file_path, start, end):
    """
    根据起始和结束行号（1-based）从文件中读取行内容。
    """
    if not os.path.exists(file_path):
        return f"文件不存在: {file_path}"

    with open(file_path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    # start 和 end 是 1-based 的
    return "".join(all_lines[max(0, start-1):min(len(all_lines), end)])

def generate_prompt(template_path, source_dir, kg_path, task_file_path, task_line, meta_path):
    """
    解析 TASK 文件中的一行，并填充提示词模板。
    """
    try:
        # 1. 解析任务行
        # 格式: - [ ] filename | 前序行[ctx_range] | 当前处理行[current_range] | [ID: chunk_id]
        parts = task_line.split('|')
        filename = parts[0].replace('- [ ]', '').strip()
        ctx_range = parts[1].replace('前序行', '').strip(' []')
        cur_range = parts[2].replace('当前处理行', '').strip(' []')

        chunk_id = ""
        if len(parts) > 3 and "ID:" in parts[3]:
            chunk_id = parts[3].replace('ID:', '').strip(' []')
        else:
            chunk_id = f"{filename}_{cur_range.replace('~', '-')}"

        file_path = os.path.join(source_dir, filename)

        # 2. 读取语料内容
        ctx_content = ""
        if "无前序背景" not in ctx_range:
            c_start, c_end = map(int, ctx_range.split('~'))
            ctx_content = get_lines(file_path, c_start, c_end)

        cur_start, cur_end = map(int, cur_range.split('~'))
        cur_content = get_lines(file_path, cur_start, cur_end)

        # 3. 读取并填充模板
        with open(template_path, 'r', encoding='utf-8') as tf:
            template = tf.read()

        tools_help = get_memocli_tools_help(chunk_id)

        prompt = template.replace('{{chunk_id}}', chunk_id)
        prompt = prompt.replace('{{context_content}}', ctx_content or "（无前序背景）")
        prompt = prompt.replace('{{current_content}}', cur_content)
        prompt = prompt.replace('{{kg_path}}', kg_path)
        prompt = prompt.replace('{{task_file_path}}', task_file_path)
        prompt = prompt.replace('{{filename}}', filename)
        prompt = prompt.replace('{{line_range}}', f"{cur_start}-{cur_end}")

        # 4. 注入独立的工具帮助
        for key, value in tools_help.items():
            prompt = prompt.replace('{{' + key + '}}', value)

        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta_content = mf.read()
                prompt = prompt.replace('{{meta_content}}', meta_content)

        # 5. 保存调试日志
        debug_dir = os.path.join(kg_path, "debug_log")
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)

        safe_chunk_id = chunk_id.replace('/', '_').replace(' ', '_')
        debug_path = os.path.join(debug_dir, f"subagent_prompt_{safe_chunk_id}.md")
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

        return f"--- PROMPT SAVED TO: {debug_path} ---\n\n{prompt}"

    except Exception as e:
        import traceback
        return f"生成提示词时出错: {str(e)}\n{traceback.format_exc()}"

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("用法: python generate_prompt.py <模板路径> <源语料目录> <知识库路径> <任务文件路径> \"<任务行内容>\" <Meta路径>")
    else:
        # 参数顺序: 模板, 语料目录, 知识库, 任务文件, 任务行, Meta
        result = generate_prompt(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print(result)
