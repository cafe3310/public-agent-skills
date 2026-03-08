import os
import sys
import argparse

def pre_check(files, n_lines):
    # Enforce 3 files limit as requested
    if len(files) > 3:
        print(f"Error: Too many files ({len(files)}). Maximum 3 files are allowed per run. / 错误：文件数量过多 ({len(files)})。每次运行最多允许 3 个文件。")
        sys.exit(1)

    for file_path in files:
        if not os.path.exists(file_path):
            print(f"Error: File not found / 文件未找到: {file_path}")
            continue
        
        file_name = os.path.basename(file_path)
        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            total_lines = len(lines)
            preview_content = "".join(lines[:n_lines])
        
        print(f"===FILE_START {file_name} - 文件大小:{file_size_kb}KB - 总行数:{total_lines}行 - 以下是前{n_lines}行，用 read-file 查看全文===")
        print(preview_content)
        print(f"===FILE_END {file_name}===")
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-check Obsidian documents.")
    parser.add_argument("files", nargs="+", help="File paths to check (Max 3 per run).")
    parser.add_argument("--lines", type=int, default=15, help="Number of lines to preview.")
    
    args = parser.parse_args()
    pre_check(args.files, args.lines)
