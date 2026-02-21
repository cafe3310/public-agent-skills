import os
import argparse
import yaml
import re
import sys
import difflib
from datetime import datetime
from pathlib import Path

# Add the workflows/01_ingest directory to sys.path to import SCRIPT_util
sys.path.append(str(Path(__file__).parent.parent / "01_ingest"))
from SCRIPT_util import RegexPatterns, KnowledgeBasePaths

def parse_args():
    parser = argparse.ArgumentParser(description="[知识生成] 组装上下文与提示词，输出到 stdout 供 LLM Agent 读取。")
    parser.add_argument("--base-dir", default="vault", help="知识库根目录 (例如 vault 或 kb)")
    parser.add_argument("--spec-file", required=True, help="项目定义文件路径 (02-project-specs)")
    parser.add_argument("--data-dir", help="数据源目录 (默认: {base_dir}/01-chats-input-organized)")
    parser.add_argument("--output-dir", help="输出目录 (默认: {base_dir}/04-output-documents)")
    parser.add_argument("--force-full", action="store_true", help="强制执行全量提取，即使 strategy 为 incremental")
    return parser.parse_args()

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_chat_logs(source_dir, start_date, end_date):
    """
    获取指定日期范围内的聊天记录。
    返回: [(filename, content), ...]
    """
    logs = []
    source_path = Path(source_dir)
    if not source_path.exists():
        return logs

    # 简单策略：文件名通常是 YYYY-MM.md
    for md_file in source_path.glob("*.md"):
        try:
            file_name = md_file.stem # "2023-10"
            # 尝试解析文件名中的日期
            try:
                file_date = datetime.strptime(file_name, "%Y-%m")
                # 月份粒度的简单筛选
                file_month_start = file_date
                if file_date.month == 12:
                    file_month_end = file_date.replace(year=file_date.year+1, month=1)
                else:
                    file_month_end = file_date.replace(month=file_date.month+1)

                # 检查时间是否有重叠
                if file_month_end < start_date or file_month_start > end_date:
                    continue
            except ValueError:
                # 如果文件名不是日期格式，暂时默认包含
                pass

            with open(md_file, 'r', encoding='utf-8') as f:
                logs.append((md_file.name, f.read()))

        except Exception as e:
            # 忽略读取错误，避免中断
            continue

    return logs

def main():
    args = parse_args()
    base_dir = args.base_dir
    data_dir = args.data_dir if args.data_dir else os.path.join(base_dir, "01-chats-input-organized")
    output_base_dir = args.output_dir if args.output_dir else os.path.join(base_dir, "04-output-documents")

    # 1. 加载项目定义
    spec = load_yaml(args.spec_file)
    project_id = spec['meta']['id']
    project_name = spec['meta']['name']
    strategy = spec['meta'].get('strategy', 'full')

    # 提取时间范围
    time_range = spec['scope']['time_range']
    start_date = datetime.strptime(time_range['start'], "%Y-%m-%d")
    end_date_str = time_range.get('end')
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        # 如果未定义结束日期，则默认为当前时间
        end_date = datetime.now()

    # 2. 收集上下文并写入 contexts.md
    all_context = []
    for src in spec['scope']['sources']:
        src_name = src['name'] if isinstance(src, dict) else src
        src_name = RegexPatterns.chat_name_sanitize(src_name)
        source_path = Path(data_dir) / src_name

        logs = get_chat_logs(source_path, start_date, end_date)
        for fname, content in logs:
            header = f"\n\n# 数据来源: {src_name}/{fname}\n"
            all_context.append(header)
            all_context.append(content)

    combined_context = "".join(all_context)

    # 3. 准备输出目录
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    run_parent_dir = Path(output_base_dir) / project_id
    run_dir = run_parent_dir / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 寻找上一次运行的目录以计算增量
    previous_run_dir = None
    if run_parent_dir.exists():
        runs = sorted([d for d in run_parent_dir.iterdir() if d.is_dir() and d.name.startswith("run_") and d != run_dir], reverse=True)
        if runs:
            previous_run_dir = runs[0]

    context_file = run_dir / "contexts.md"
    with open(context_file, 'w', encoding='utf-8') as f:
        f.write(combined_context)

    # 生成 added-contexts.md (增量上下文)
    added_context_file = None
    if strategy == 'incremental' and not args.force_full:
        if not previous_run_dir:
            print(f"STATUS: FIRST_INCREMENTAL_RUN")
            print(f"REASON: 未发现项目 {project_id} 的历史运行记录。也许需要先用 force-full 参数执行一次全量提取以建立基线。")
            sys.exit(0)

        prev_context_file = previous_run_dir / "contexts.md"
        if not prev_context_file.exists():
            print(f"STATUS: FIRST_INCREMENTAL_RUN")
            print(f"REASON: 历史目录 {previous_run_dir} 中缺失 contexts.md。")
            sys.exit(0)

        with open(prev_context_file, 'r', encoding='utf-8') as f:
            prev_lines = f.readlines()
        curr_lines = combined_context.splitlines(keepends=True)

        # 使用 difflib 计算新增部分 (仅保留以 '+' 开头的行)
        diff = list(difflib.unified_diff(prev_lines, curr_lines, n=0))
        added_lines = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]

        if not added_lines:
            print(f"STATUS: 增量模式终止。当前语料库与上次运行 ({previous_run_dir.name}) 相比无任何新增内容。")
            # 清理本次生成的空目录
            import shutil
            shutil.rmtree(run_dir)
            sys.exit(0)

        added_context_file = run_dir / "added-contexts.md"
        with open(added_context_file, 'w', encoding='utf-8') as f:
            f.writelines(added_lines)
        print(f"INFO: 增量提取模式已激活。发现 {len(added_lines)} 行新内容。")

    # 如果强制全量，即使 strategy 定义为 incremental 也会走 full 流程
    if args.force_full:
        strategy = 'full'
        print("INFO: 强制执行全量提取模式。")

    # 决定本次提取使用的上下文路径
    active_context_file = added_context_file if (strategy == 'incremental' and not args.force_full) else context_file

    # 4. 为每个目标生成分阶段 Prompt 文件与状态文件
    goals = spec.get('extraction_goals', [])
    generated_prompts = []
    previous_outputs = []

    # 同步任务目录结构 - 使用 KnowledgeBasePaths
    tasks_run_dir = Path(KnowledgeBasePaths.get_task_run_dir(project_id, base_dir))

    for idx, goal in enumerate(goals, 1):
        goal_title = goal['title']
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', goal_title).strip()
        prompt_filename = f"prompts-{idx:02d}-{safe_title}.md"
        output_filename = f"output-{idx:02d}-{safe_title}.md"
        state_filename = f"task_{idx:02d}.yaml"

        prompt_path = run_dir / prompt_filename
        output_path = run_dir / output_filename
        state_path = tasks_run_dir / state_filename

        dep_path = previous_outputs[-1] if previous_outputs else None

        # 构建包含指令的 YAML 状态文件
        state_content = f"""# [SUB-AGENT INSTRUCTION]
# 你正在执行任务：{goal_title}。
# 1. 初始化: 若 total_chunks 为 -1，请先使用 read_file 获取 context_path 的总行数，按每 1000 行一个 chunk 分割，并初始化下面的 chunk_list。
# 2. 隔离提取: 遍历 chunk_list，处理 status 为 pending 的块，将产出保存为独立文件：output-{idx:02d}-chunk-{{{{chunk_no}}}}.md。
# 3. 状态同步: 每处理并成功写入一个分块文件，请务必更新对应 chunk 的 status 为 done 并同步此文件。
# 4. 严禁合并: 此阶段严禁尝试将分块合并为单个文件。

meta:
  project_id: "{project_id}"
  run_id: "run_{timestamp}"
  stage_title: "{goal_title}"
  strategy: "{strategy}"

files:
  context_path: "{active_context_file}"
  prompt_path: "{prompt_path}"
  run_dir: "{run_dir}" # 分块结果存放地
  dependency_path: "{dep_path if dep_path else ''}"

progress:
  total_chunks: -1
  chunk_list: [] # 格式: - chunk_no: 1, file: contexts.md, lines: 1-1000, status: pending
  status: "PENDING"
"""
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(state_content)

        # 构建原子指令内容 (Stage-specific)
        instructions = [
            f"# Extraction Goal {idx}: {goal_title}",
            f"## Target",
            f"{goal['prompt']}",
            "",
            f"## Files (Auto-mapped in State File)",
            f"- Output: `{output_path}`",
            f"- Context: `{active_context_file}`",
            f"- State: `{state_path}`"
        ]

        if dep_path:
            instructions.append(f"- Dependencies: `{dep_path.name}`")

        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(instructions))

        generated_prompts.append({
            'idx': idx,
            'title': goal_title,
            'prompt_path': prompt_path,
            'output_path': output_path,
            'state_path': state_path,
            'dep_path': dep_path,
            'active_context': active_context_file
        })
        previous_outputs.append(output_path)

    # 5. 输出 Sub-agent 启动提示词列表
    print(f"DEBUG: 任务目录已就绪: {run_dir}")
    print("\n" + "="*40)
    print("ACTION REQUIRED: 请按顺序通过 im-local-db_knowledge-extractor 子代理启动任务")

    for item in generated_prompts:
        print(f"\n>>> 阶段 {item['idx']}: {item['title']} <<<")
        print(f"请启动 `im-local-db_knowledge-extractor` 子代理执行以下指令：")
        print(f"  prompt_path: \"{item['prompt_path']}\"")
        print(f"  context_path: \"{item['active_context']}\"")
        print(f"  state_path: \"{item['state_path']}\"")
        print(f"  output_dir: \"{run_dir}\"")
        if item['dep_path']:
            print(f"  dependency_path: \"{item['dep_path']}\"")

    print("\n" + "="*40)
    print("DONE: 提取任务准备就绪。")
    print("QUESTION: 提取完成后，您希望如何生成最终报告？")
    print("  1. [标准总结] 按照 (时间轴/关键决策/遗留事项) 结构生成报告。")
    print("  2. [自定义结构] 我将提供特定的报告框架或关注点。")
    print("  3. [纯提取] 仅保留分阶段提取结果，无需汇总报告。")
    print("请在所有子代理任务状态为 COMPLETED 后告知我您的选择。")
    print("="*40)

if __name__ == "__main__":
    main()
