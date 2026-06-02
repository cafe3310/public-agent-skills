import os
import sys
import glob
import yaml

def merge_yamls(work_dir):
    input_base_dir = os.path.join(work_dir, "03-ocr")
    output_dir = os.path.join(work_dir, "04-merged")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_base_dir):
        print(f"错误: 输入目录不存在 {input_base_dir}")
        return

    dirs = sorted([d for d in os.listdir(input_base_dir) if os.path.isdir(os.path.join(input_base_dir, d))])

    for d in dirs:
        current_input_dir = os.path.join(input_base_dir, d)
        print(f"处理目录: {d} ...")
        
        yaml_files = sorted(glob.glob(os.path.join(current_input_dir, "*.yaml")))
        merged_data = []
        seen_names = set()
        
        for yf in yaml_files:
            try:
                with open(yf, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'name' in item:
                                name = item['name']
                                if name not in seen_names:
                                    merged_data.append(item)
                                    seen_names.add(name)
            except Exception:
                pass

        if merged_data:
            output_path = os.path.join(output_dir, f"{d}.yaml")
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(merged_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            print(f"  -> 生成: {output_path} ({len(merged_data)} 条)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python merge.py <工作目录>")
        sys.exit(1)
    merge_yamls(sys.argv[1])
