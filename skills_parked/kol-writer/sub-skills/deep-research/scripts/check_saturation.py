import sys
import os
import json
import re
from urllib.parse import urlparse

def check_saturation(task_dir):
    fragments_path = os.path.join(task_dir, "knowledge_fragments.md")
    spec_path = os.path.join(task_dir, "task_spec.json")

    if not os.path.exists(fragments_path):
        return "Continue: knowledge_fragments.md not found. Agent hasn't recorded facts yet."
    
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
            print(f"Warning: Could not parse task_spec.json - {e}")
            pass
    
    print(f"--- Saturation Report for {os.path.basename(task_dir)} ---")
    print(f"Domains found: {len(domains)} (Target: >= 5)")
    print(f"Facts extracted: {fact_count} (Target: >= 10)")
    
    is_saturated = True
    
    if missing_keywords:
        print(f"Keyword Coverage: {coverage*100:.0f}% (Target: 100%)")
        print(f"Missing aspects: {', '.join(missing_keywords)}")
        is_saturated = False
        
    if len(domains) < 5 or fact_count < 10:
        is_saturated = False
        
    print("-" * 40)
    if is_saturated:
        return "Status: Saturated"
    else:
        return f"Status: Continue (Need more diverse sources or coverage of missing aspects)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_saturation.py <task_dir>")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory.")
        sys.exit(1)
        
    print(check_saturation(target_dir))
