import sys
import os
import json
import re
from urllib.parse import urlparse

def check_saturation(task_dir):
    fragments_path = os.path.join(task_dir, "knowledge_fragments.md")
    spec_path = os.path.join(task_dir, "task_spec.json")

    if not os.path.exists(fragments_path):
        return "Status: Continue (状态: 继续，未找到 knowledge_fragments.md。代理尚未记录任何事实。)"
    
    with open(fragments_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Source Diversity
    # Find all HTTP/HTTPS URLs in the text
    urls = re.findall(r'(https?://[^\s\]\>]+)', content)
    domains = set(urlparse(url).netloc for url in urls)
    
    # 2. Fact Count (Heuristic: count lines or blocks starting with bullets)
    fact_count = len(re.findall(r'^[-*]\s+', content, re.MULTILINE))
    
    # 3. Keyword Coverage (if task_spec.json exists)
    coverage = 0
    missing_keywords = []
    if os.path.exists(spec_path):
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            keywords = spec.get("keywords", [])
            if keywords:
                found = sum(1 for kw in keywords if kw.lower() in content.lower())
                coverage = found / len(keywords)
                missing_keywords = [kw for kw in keywords if kw.lower() not in content.lower()]
        except Exception as e:
            print(f"警告: 无法解析 task_spec.json - {e}")
            pass
    
    print(f"--- {os.path.basename(task_dir)} 饱和度报告 ---")
    print(f"发现的域名数: {len(domains)} (目标: >= 5)")
    print(f"提取的事实数: {fact_count} (目标: >= 10)")
    
    is_saturated = True
    
    if missing_keywords:
        print(f"关键词覆盖率: {coverage*100:.0f}% (目标: 100%)")
        print(f"缺失的维度: {', '.join(missing_keywords)}")
        is_saturated = False
        
    if len(domains) < 5 or fact_count < 10:
        is_saturated = False
        
    print("-" * 40)
    if is_saturated:
        return "Status: Saturated (状态: 已饱和)"
    else:
        return f"Status: Continue (状态: 继续，需要更丰富的数据源或覆盖缺失的维度)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_saturation.py <task_dir>")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"错误: {target_dir} 不是一个有效的目录。")
        sys.exit(1)
        
    print(check_saturation(target_dir))
