import os
import sys
import yaml
import glob

def analyze_groups(work_dir):
    input_dir = os.path.join(work_dir, "05-classified")
    report_dir = os.path.join(work_dir, "06-report")
    
    if not os.path.exists(input_dir):
        print(f"错误: 目录 '{input_dir}' 不存在。")
        return
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # 1. 识别 'everything' 文件
    # 约定：文件名包含 'everything'
    yaml_files = glob.glob(os.path.join(input_dir, "*.yaml"))
    everything_files = [f for f in yaml_files if "everything" in os.path.basename(f).lower()]
    
    if len(everything_files) != 1:
        print("错误: 请确保 '05-classified' 目录中包含唯一的一个 'everything' 文件。")
        return
    
    everything_path = everything_files[0]
    other_files = [f for f in yaml_files if f != everything_path]
    print(f"主文件: {os.path.basename(everything_path)}")

    # 2. 建立索引 (Item -> List of Groups)
    name_to_groups = {}
    
    # 同时收集所有出现过的 Group Names (文件名)
    all_group_names = [] 

    for fpath in other_files:
        group_name = os.path.splitext(os.path.basename(fpath))[0]
        all_group_names.append(group_name)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or []
                for item in data:
                    if isinstance(item, dict) and 'name' in item:
                        name = item['name']
                        if name not in name_to_groups: name_to_groups[name] = []
                        if group_name not in name_to_groups[name]: name_to_groups[name].append(group_name)
        except: pass

    # 3. 注入属性 & 全局查漏
    uncategorized_people = []
    uncategorized_groups = []
    
    try:
        with open(everything_path, 'r', encoding='utf-8') as f:
            all_items = yaml.safe_load(f) or []
            
        for item in all_items:
            if isinstance(item, dict) and 'name' in item:
                groups = name_to_groups.get(item['name'], [])
                item['groups'] = groups
                
                # 如果没有任何分组，则视为未分类
                if not groups:
                    itype = item.get('type')
                    if itype == 'people': uncategorized_people.append(item)
                    elif itype == 'group': uncategorized_groups.append(item)
        
        # 更新 everything 文件
        with open(everything_path, 'w', encoding='utf-8') as f:
            yaml.dump(all_items, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # 输出全局报告
        with open(os.path.join(report_dir, "uncategorized_people.yaml"), 'w', encoding='utf-8') as f:
            yaml.dump(uncategorized_people, f, allow_unicode=True, sort_keys=False)
        with open(os.path.join(report_dir, "uncategorized_groups.yaml"), 'w', encoding='utf-8') as f:
            yaml.dump(uncategorized_groups, f, allow_unicode=True, sort_keys=False)
            
        print(f"全局查漏完成: 人({len(uncategorized_people)}), 群({len(uncategorized_groups)})")

        # 4. 层级漏斗分析 (通用版)
        # 逻辑：
        # - 用户可能有一级分类（包含全量）和二级分类（包含部分）。
        # - 任何在一级分类中，但不在该一级分类下属的任何二级分类中的项目，都是“漏斗未处理”。
        # - 由于脚本无法自动知道哪些是二级，这里通过打印简单的包含关系矩阵，或提示用户。
        # - (高级)：尝试通过前缀匹配。例如 'ppl-contact' vs 'ppl-vip'。
        #   如果 'ppl-contact' 包含 'ppl-vip' 的所有项目，则 'ppl-contact' 是一级。
        
        # 简化策略：提示用户查看全局报告即可，层级分析留给用户自行比对，或后续增加专门的 config。
        print("提示: 报告已生成至 06-report。请检查 uncategorized_*.yaml 进行查漏补缺。")

    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python analyze.py <工作目录>")
        sys.exit(1)
    analyze_groups(sys.argv[1])
