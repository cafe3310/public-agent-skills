import sys
import os
import time
import random
import subprocess
import json
import re
import shutil
import platform

# 检测操作系统
IS_WINDOWS = platform.system() == "Windows"

def check_dependencies():
    """检查必要的依赖环境"""
    has_npm = shutil.which("npm") or (IS_WINDOWS and shutil.which("npm.cmd"))
    cmd_name = "agent-browser"
    has_ab = shutil.which(cmd_name) or (IS_WINDOWS and shutil.which(f"{cmd_name}.cmd"))
    
    if not has_npm:
        print("错误: 未找到 'npm'。这通常需要安装 Node.js。")
        print("AGENT_ACTION_REQUIRED:ASK_INSTALL_NPM")
        sys.exit(1)
        
    if not has_ab:
        print(f"错误: 未找到 '{cmd_name}' 命令。")
        print("AGENT_ACTION_REQUIRED:ASK_INSTALL_AGENT_BROWSER")
        sys.exit(1)
    
    print("正在检查 agent-browser 环境...")
    try:
        # Windows 下 subprocess.run 推荐配合 shell=True 使用以识别 npm 命令
        subprocess.run(["agent-browser", "doctor", "--offline", "--quick"], 
                       capture_output=True, check=True, shell=IS_WINDOWS)
    except subprocess.CalledProcessError:
        print("警告: 'agent-browser doctor' 检查未完全通过，建议运行 'agent-browser doctor --fix'。")

def run_command(cmd):
    """执行命令并捕获输出，适配 Windows shell"""
    print(f"执行命令: {' '.join(cmd)}")
    try:
        # shell=IS_WINDOWS 解决了 Windows 下无法直接运行 npm 全局命令的问题
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=IS_WINDOWS)
        if result.returncode != 0:
            print(f"命令返回错误码 {result.returncode}: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"错误: 命令执行超时")
        return ""
    except Exception as e:
        print(f"错误: 执行命令时发生异常: {e}")
        return ""

def ensure_autoconnect_config():
    """确保 agent-browser 全局配置中开启了 autoConnect，以优先连接真实浏览器"""
    config_dir = os.path.expanduser("~/.agent-browser")
    config_path = os.path.join(config_dir, "config.json")
    
    # 确保目录存在
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except Exception as e:
            print(f"无法创建配置目录: {e}")
            return

    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            pass # 损坏则覆盖

    # 如果没有设置或不是 true，则强制写入
    if config.get("autoConnect") is not True:
        print(f"正在配置 agent-browser 以优先连接真实浏览器 (autoConnect: true)...")
        config["autoConnect"] = True
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"写入配置失败: {e}")

def get_metrics(url):
    """访问推文页面并提取数据"""
    # 强制使用 headed 模式
    session_cmd = ["--headed", "--session-name", "twitter-watch"]

    # 打开 URL
    run_command(["agent-browser"] + session_cmd + ["open", url])

    # 随机延迟，等待异步内容加载
    delay = random.uniform(5, 10)
    print(f"等待 {delay:.2f}秒 以确保页面完全加载...")
    time.sleep(delay)

    # 1. 检查页面是否加载成功或存在错误
    # 常见的错误信息：嗯…此页面不存在、Something went wrong、This page doesn't exist
    error_texts = ["此頁面不存在", "此页面不存在", "Something went wrong", "Hmm...this page doesn't exist", "页面已失效"]
    page_text = run_command(["agent-browser"] + session_cmd + ["snapshot", "-i", "-c"])
    for err in error_texts:
        if err in page_text:
            return {"ERROR": f"页面加载失败或推文不存在 ({err})", "URL": url}

    # 拟人化滚动：触发懒加载
    print("正在执行拟人化滚动以触发数据加载...")
    run_command(["agent-browser"] + session_cmd + ["scroll", "down", "500"])
    time.sleep(random.uniform(1.5, 2.5))
    run_command(["agent-browser"] + session_cmd + ["scroll", "up", "500"])
    time.sleep(random.uniform(1, 2))

    # 初始化指标，每个指标包含“原文”和“数值”
    metrics = {
        "查看": {"raw": "N/A", "val": 0},
        "回复": {"raw": "N/A", "val": 0},
        "转发": {"raw": "N/A", "val": 0},
        "喜欢": {"raw": "N/A", "val": 0},
        "书签": {"raw": "N/A", "val": 0}
    }

    def parse_value(text):
        """将带有 K, M, B, 万, 亿等后缀的字符串转换为数字 (支持中英文及大小写)"""
        if not text or text == "N/A": return 0
        # 统一清理
        text = text.replace(",", "").replace(" ", "").strip()
        multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000,
            '万': 10000,
            '萬': 10000,
            '亿': 100000000,
            '億': 100000000
        }
        # 提取数字部分
        num_match = re.search(r'([\d.]+)', text)
        if not num_match: return 0
        num = float(num_match.group(1))

        # 查找单位 (忽略英文大小写)
        upper_text = text.upper()
        for unit, mult in multipliers.items():
            if unit in upper_text:
                return int(num * mult)
        return int(num)

    try:
        # 优先级 1: data-testid (官方/最精确)
        selectors = {
            "回复": 'button[data-testid="reply"]',
            "转发": 'button[data-testid="retweet"]',
            "喜欢": 'button[data-testid="like"]',
            "书签": 'button[data-testid="bookmark"]',
            "查看": 'a[href*="/analytics"]'
        }

        for metric, selector in selectors.items():
            val = run_command(["agent-browser"] + session_cmd + ["get", "text", selector])
            if not (val and any(char.isdigit() for char in val)):
                val = run_command(["agent-browser"] + session_cmd + ["get", "attr", selector, "aria-label"])

            if val:
                # 提取原始数值描述，允许空格及所有支持的单位
                match = re.search(r'([\d.,]+\s*[KkMmBb+万亿萬億]?)', val)
                if match:
                    raw_str = match.group(1).strip()
                    metrics[metric] = {"raw": raw_str, "val": parse_value(raw_str)}
                    continue

        # 优先级 2: 如果还是 N/A，尝试模糊匹配 aria-label
        label_map = {
            "回复": ["reply", "回覆", "回复"],
            "转发": ["retweet", "轉發", "转发"],
            "喜欢": ["like", "喜歡", "喜欢", "點讚", "点赞"],
            "书签": ["bookmark", "書籤", "书签"],
            "查看": ["view", "查看", "觀看", "分析"]
        }

        for metric, labels in label_map.items():
            if metrics[metric]["raw"] != "N/A": continue
            for label in labels:
                for tag in ["button", "a", "div", "span"]:
                    attr_val = run_command(["agent-browser"] + session_cmd + ["get", "attr", f'{tag}[aria-label*="{label}"]', "aria-label"])
                    if attr_val:
                        # 模式：数字在前或在后，允许空格及所有单位
                        pattern = rf'([\d.,]+\s*[KkMmBb+万亿萬億]?)\s*.*?{label}|{label}.*?\s*([\d.,]+\s*[KkMmBb+万亿萬億]?)'
                        m = re.search(pattern, attr_val, re.IGNORECASE)
                        if m:
                            raw_str = (m.group(1) or m.group(2)).strip()
                            if raw_str:
                                metrics[metric] = {"raw": raw_str, "val": parse_value(raw_str)}
                                break
                if metrics[metric]["raw"] != "N/A": break

    except Exception as e:
        print(f"抓取数据时发生异常 ({url}): {e}")

    return metrics

def get_tweet_id(url):
    """从 URL 中提取推文 ID，并清理 Windows 不合规字符"""
    # 提取 status 后的数字
    match = re.search(r'status/(\d+)', url)
    if match:
        return match.group(1)
    
    # 如果不是标准 status 链接，则清理末尾部分作为文件名
    # Windows 不允许 \ / : * ? " < > |
    slug = url.split('/')[-1].split('?')[0] # 移除查询参数
    safe_slug = re.sub(r'[\/\\:\*\?\"<>\|]', '_', slug)
    return safe_slug

def verify_real_browser():
    """快速验证 agent-browser 处于‘非测试模式’且连接已建立"""
    # 强制 headed 模式
    session_cmd = ["--headed", "--session-name", "twitter-watch"]
    
    # 尝试获取浏览器 user-agent
    ua = run_command(["agent-browser"] + session_cmd + ["eval", "navigator.userAgent"])
    if not ua:
        print("错误: 无法获取浏览器信息。")
        print("请确保你已运行验证步骤（打开 Google 并点击‘允许调试连接’）。")
        print("如果仍然无法连接，请尝试在浏览器中访问 chrome://inspect/#remote-debugging 以启用 Remote Debugging。")
        sys.exit(1)
    
    if "Headless" in ua:
        print("警告: 检测到浏览器仍处于无头(Headless)模式，这可能导致抓取失败。")
    else:
        print(f"环境验证通过 (非无头模式): {ua}")

def main():
    check_dependencies()
    # 自动设置配置
    ensure_autoconnect_config()
    
    # 1. 引导 Agent 进行手动确认
    verify_real_browser()
    
    if len(sys.argv) < 2:
        print("用法: python3 watch.py <链接文件>")
        sys.exit(1)
        
    links_file = sys.argv[1]
    if not os.path.exists(links_file):
        print(f"错误: 文件不存在: {links_file}")
        sys.exit(1)
        
    with open(links_file, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]
        
    results = []
    
    for link in links:
        tweet_id = get_tweet_id(link)
        output_file = f"output_{tweet_id}.json"
        
        # 检查是否已有结果（断点续传逻辑）
        if os.path.exists(output_file):
            print(f"\n跳过已处理的链接: {link} (已存在 {output_file})")
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results.append(json.load(f))
                continue
            except Exception:
                pass # 如果文件损坏则重新抓取

        print(f"\n[任务] 正在处理: {link}")
        data = get_metrics(link)
        data['URL'] = link
        results.append(data)
        
        # 实时保存
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"结果已保存至 {output_file}")
        except Exception as e:
            print(f"保存结果时出错: {e}")
        
    # 生成汇总报告
    report_file = "twitter_report.md"
    print(f"\n正在生成汇总报告: {report_file}...")
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Twitter 互动数据监控报告\n\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {platform.system()} {platform.release()}\n")
            f.write(f"总计处理: {len(results)} 条链接\n\n")
            f.write("| URL | 状态 | 查看 | 回复 | 转发 | 喜欢 | 书签 |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
            for res in results:
                display_url = (res['URL'][:47] + '...') if len(res['URL']) > 50 else res['URL']
                
                if "ERROR" in res:
                    f.write(f"| [{display_url}]({res['URL']}) | ❌ {res['ERROR']} | - | - | - | - | - |\n")
                else:
                    def fmt(metric):
                        m = res.get(metric, {"raw": "N/A", "val": 0})
                        if m["raw"] != "N/A":
                            return f"{m['raw']} ({m['val']:,})"
                        return "N/A"
                    f.write(f"| [{display_url}]({res['URL']}) | ✅ 成功 | {fmt('查看')} | {fmt('回复')} | {fmt('转发')} | {fmt('喜欢')} | {fmt('书签')} |\n")
        print(f"\n[完成] 汇总报告已就绪。")
    except Exception as e:
        print(f"生成报告时出错: {e}")

    # 同样在关闭时显式指定会话
    run_command(["agent-browser", "--session-name", "twitter-watch", "close", "--all"])

if __name__ == "__main__":
    main()