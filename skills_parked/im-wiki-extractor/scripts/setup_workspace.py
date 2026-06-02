import os
import sys
from datetime import datetime

def setup_task(source_dir, task_file_path):
    """
    扫描目录下的 MD 文件，按文件名排序，生成带有分片和上下文的 TASK 状态文件。
    来源文件按顺序排列，状态文件的每行包含文件名、前序行范围和当前处理行范围。
    """
    # 获取并排序所有的 markdown 源文件
    files = sorted([f for f in os.listdir(source_dir) if f.endswith('.md')])
    if not files:
        print(f"错误: 在目录 {source_dir} 中未找到任何 .md 文件")
        return

    with open(task_file_path, 'w', encoding='utf-8') as task_f:
        task_f.write(f"# 群聊知识图谱提取任务清单\n")
        task_f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        task_f.write("## 任务列表\n\n")
        task_f.write("> 格式: - [ ] 文件名 | 前序行[起始~结束, 50行] | 当前处理行[起始~结束, 100行]\n\n")

        for filename in files:
            file_path = os.path.join(source_dir, filename)
            
            # 流式统计行数
            total_lines = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in f:
                    total_lines += 1
            
            chunk_size = 100
            context_size = 50
            
            # 分片切分
            for i in range(0, total_lines, chunk_size):
                start = i + 1
                end = min(i + chunk_size, total_lines)
                
                # 计算上下文
                if i == 0:
                    ctx_str = "无前序背景"
                else:
                    ctx_start = max(1, i - context_size + 1)
                    ctx_end = i
                    ctx_str = f"{ctx_start}~{ctx_end}"
                
                # 显式生成 chunk_id
                chunk_id = f"{filename}_{start}-{end}"
                task_f.write(f"- [ ] {filename} | 前序行[{ctx_str}] | 当前处理行[{start}~{end}] | [ID: {chunk_id}]\n")

    print(f"成功生成任务状态文件: {task_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python setup_workspace.py <源语料目录> <状态文件路径>")
    else:
        setup_task(sys.argv[1], sys.argv[2])
