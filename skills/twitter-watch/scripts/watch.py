import sys
import os
import time
import random
import subprocess
import json
import re

def run_command(cmd):
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    return result.stdout.strip()

def get_metrics(url):
    # 使用特定会话以保持状态
    session_cmd = ["--session-name", "twitter-watch"]
    
    # 打开 URL
    run_command(["agent-browser"] + session_cmd + ["open", url])
    
    # 随机延迟 3-7秒，等待页面加载
    delay = random.uniform(3, 7)
    print(f"等待 {delay:.2f}秒 以确保页面加载...")
    time.sleep(delay)
    
    # 拟人化滚动
    # 先向下滚动再向上滚动，触发动态内容并模拟真人行为
    run_command(["agent-browser"] + session_cmd + ["scroll", "down", "400"])
    time.sleep(random.uniform(1, 2))
    run_command(["agent-browser"] + session_cmd + ["scroll", "up", "400"])
    time.sleep(random.uniform(1, 2))
    
    metrics = {
        "查看": "N/A",
        "回复": "N/A",
        "转发": "N/A",
        "喜欢": "N/A",
        "书签": "N/A"
    }

    try:
        # Twitter 通常将这些数据存储在 aria-label 或特定的 test-id 中
        # 我们优先尝试 test-id，如果失败则回退到 aria-label
        
        selectors = {
            "回复": 'div[data-testid="reply"]',
            "转发": 'div[data-testid="retweet"]',
            "喜欢": 'div[data-testid="like"]',
            "书签": 'div[data-testid="bookmark"]',
            "查看": 'a[href*="/analytics"]'
        }
        
        for metric, selector in selectors.items():
            val = run_command(["agent-browser"] + session_cmd + ["get", "text", selector])
            if val:
                # 清理数据: 例如 "1.2K Likes" -> "1.2K"
                metrics[metric] = val.strip()
            else:
                # 如果 testid 失败，尝试通过 aria-label 回退（支持中英文标签）
                label_map = {
                    "回复": ["reply", "回复"],
                    "转发": ["retweet", "转发"],
                    "喜欢": ["like", "喜欢", "点赞"],
                    "书签": ["bookmark", "书签"],
                    "查看": ["view", "查看"]
                }
                
                found = False
                for label in label_map[metric]:
                    val = run_command(["agent-browser"] + session_cmd + ["get", "attr", f'[aria-label*="{label}"]', "aria-label"])
                    if val:
                        # 从 "1,234 likes" 或 "1,234 次赞" 中提取数字
                        match = re.search(r'([\d.,KM]+)', val)
                        if match:
                            metrics[metric] = match.group(1)
                            found = True
                            break
                if found: continue

    except Exception as e:
        print(f"提取数据时出错 ({url}): {e}")

    return metrics

def main():
    if len(sys.argv) < 2:
        print("用法: python3 watch.py <链接文件>")
        sys.exit(1)
        
    links_file = sys.argv[1]
    if not os.path.exists(links_file):
        print(f"文件不存在: {links_file}")
        sys.exit(1)
        
    with open(links_file, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
        
    results = []
    
    for link in links:
        print(f"\n正在处理: {link}")
        metrics = get_metrics(link)
        metrics['URL'] = link
        results.append(metrics)
        
        # 保存单条结果
        slug = re.sub(r'\W+', '_', link.split('/')[-1])
        output_file = f"output_{slug}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"数据已保存至 {output_file}")
        
    # 整合结果生成报告
    report_file = "twitter_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Twitter 互动数据监控报告\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| URL | 查看 | 回复 | 转发 | 喜欢 | 书签 |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for res in results:
            f.write(f"| {res['URL']} | {res['查看']} | {res['回复']} | {res['转发']} | {res['喜欢']} | {res['书签']} |\n")
            
    print(f"\n汇总报告已生成: {report_file}")
    run_command(["agent-browser", "close", "--all"])

if __name__ == "__main__":
    main()