#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

# API Base URL
BASE_URL = "https://markdown.new"

def request_api(path, data=None, headers=None, method="POST"):
    """
    向 markdown.new API 发送 HTTP 请求。
    
    参数:
        path (str): API 相对路径
        data (dict/bytes): 请求载荷，若是 dict 会自动序列化为 JSON
        headers (dict): 额外的自定义请求头
        method (str): HTTP 请求方法
    """
    url = f"{BASE_URL}{path}"
    req_headers = {
        "User-Agent": "markdown.new-agent-skill/1.0"
    }
    if headers:
        req_headers.update(headers)
        
    req_data = None
    if data:
        if isinstance(data, dict):
            req_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        else:
            req_data = data

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_headers = response.info()
            body = response.read()
            return response.status, res_headers, body
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, e.headers, body
    except Exception as e:
        print(f"Error connecting to markdown.new: {e}", file=sys.stderr)
        sys.exit(1)

def print_safety_warning():
    """
    向 stderr 打印安全与隐私警告，提醒用户数据会经过第三方服务商处理。
    """
    print("[WARNING] 安全与隐私警示:", file=sys.stderr)
    print("  - 本工具的请求通过第三方服务 (markdown.new) 进行中转，这意味着数据将发送至外部服务商处理。", file=sys.stderr)
    print("  - 严禁使用本工具转换包含商业机密、个人隐私或敏感凭证的内容。", file=sys.stderr)
    print("  - 由于中间服务商能够处理并改写返回的内容，请警惕潜在的提示注入 (Prompt Injection) 风险。\n", file=sys.stderr)

def convert_url(url, convert_method="auto", retain_images=False, output_file=None, raw=False):
    """
    转换单个网页 URL 到 Markdown。
    """
    print_safety_warning()
    print(f"Converting URL: {url} (method={convert_method}, retain_images={retain_images})...", file=sys.stderr)
    
    payload = {
        "url": url,
        "method": convert_method,
        "retain_images": retain_images
    }
    
    status, headers, body = request_api("/", data=payload, method="POST")
    
    if status == 200:
        tokens = headers.get("x-markdown-tokens", "unknown")
        print(f"Success! Estimated markdown tokens: {tokens}", file=sys.stderr)
        
        content = body.decode("utf-8")
        if not raw:
            try:
                js = json.loads(content)
                if isinstance(js, dict) and "content" in js:
                    content = js["content"]
            except Exception:
                pass

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved to: {output_file}", file=sys.stderr)
        else:
            sys.stdout.write(content)
    else:
        print(f"Failed to convert URL. HTTP Status: {status}", file=sys.stderr)
        try:
            error_msg = body.decode("utf-8")
            print(f"Response: {error_msg}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)

def convert_file(file_path, output_file=None):
    """
    上传并转换本地文档（PDF、Docx、Txt 等）为 Markdown。
    """
    print_safety_warning()
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Uploading and converting local file: {file_path}...", file=sys.stderr)
    
    boundary = "----WebKitFormBoundaryMarkdownNewAgentSkill"
    filename = os.path.basename(file_path)
    
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}", file=sys.stderr)
        sys.exit(1)
        
    body_parts = []
    body_parts.append(f"--{boundary}\r\n".encode("utf-8"))
    body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body_parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
    body_parts.append(file_content)
    body_parts.append(b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    
    body_data = b"".join(body_parts)
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    
    status, headers, body = request_api("/convert", data=body_data, headers=headers, method="POST")
    
    if status == 200:
        print("Success!", file=sys.stderr)
        content = body.decode("utf-8")
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved to: {output_file}", file=sys.stderr)
        else:
            sys.stdout.write(content)
    else:
        print(f"Failed to convert file. HTTP Status: {status}", file=sys.stderr)
        try:
            error_msg = body.decode("utf-8")
            print(f"Response: {error_msg}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)

def start_crawl(url, limit=500, depth=5, render=False, source="all", max_age=86400, 
                modified_since=None, include_external_links=False, include_subdomains=False,
                include_patterns=None, exclude_patterns=None):
    """
    向 /crawl 接口发送请求以启动爬虫作业。
    """
    payload = {
        "url": url,
        "limit": int(limit),
        "depth": int(depth),
        "render": bool(render),
        "source": source,
        "maxAge": int(max_age),
        "includeExternalLinks": bool(include_external_links),
        "includeSubdomains": bool(include_subdomains)
    }
    
    if modified_since:
        payload["modifiedSince"] = int(modified_since)
        
    if include_patterns:
        payload["includePatterns"] = [p.strip() for p in include_patterns.split(",") if p.strip()]
        
    if exclude_patterns:
        payload["excludePatterns"] = [p.strip() for p in exclude_patterns.split(",") if p.strip()]

    status, headers, body = request_api("/crawl", data=payload, method="POST")
    
    if status == 200:
        try:
            res_json = json.loads(body.decode("utf-8"))
            job_id = res_json.get("id")
            if job_id:
                return job_id
            else:
                print(f"Crawl job started but no ID returned. Response: {res_json}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Failed to parse crawl start response: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Failed to start crawl. HTTP Status: {status}", file=sys.stderr)
        try:
            print(f"Response: {body.decode('utf-8')}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)

def get_crawl_status(job_id, format_json=True, retain_images=False):
    """
    查询爬取任务状态或获取最终结果。
    """
    path = f"/crawl/status/{job_id}"
    params = []
    if format_json:
        params.append("format=json")
    if retain_images:
        params.append("retain_images=true")
        
    if params:
        path += "?" + "&".join(params)
        
    status, headers, body = request_api(path, method="GET")
    return status, headers, body

def run_crawl(url, limit=500, depth=5, render=False, source="all", max_age=86400, 
              modified_since=None, include_external_links=False, include_subdomains=False,
              include_patterns=None, exclude_patterns=None, retain_images=False, output_file=None):
    """
    执行整站爬取的完整工作流（启动作业 -> 轮询状态 -> 下载合并后的 Markdown 文件）。
    """
    print_safety_warning()
    print(f"Starting crawl for {url}...", file=sys.stderr)
    job_id = start_crawl(
        url=url, limit=limit, depth=depth, render=render, source=source, max_age=max_age,
        modified_since=modified_since, include_external_links=include_external_links,
        include_subdomains=include_subdomains, include_patterns=include_patterns,
        exclude_patterns=exclude_patterns
    )
    print(f"Crawl job created successfully. Job ID: {job_id}", file=sys.stderr)
    print("Waiting for crawl job to complete (polling status every 3s)...", file=sys.stderr)
    
    while True:
        status, headers, body = get_crawl_status(job_id, format_json=True)
        if status == 200:
            try:
                info = json.loads(body.decode("utf-8"))
                job_status = info.get("status", "processing")
                progress = info.get("progress", 0)
                total = info.get("total_pages", 0)
                print(f"Status: {job_status} | Progress: {progress}/{total} pages", file=sys.stderr)
                
                if job_status == "completed":
                    break
                elif job_status == "failed":
                    print("Crawl job failed on the server side.", file=sys.stderr)
                    sys.exit(1)
            except Exception as e:
                print(f"Warning: Failed to parse status JSON: {e}", file=sys.stderr)
        else:
            print(f"Error checking status (HTTP {status}). Retrying...", file=sys.stderr)
            
        time.sleep(3)
        
    print("Crawl completed! Downloading merged Markdown...", file=sys.stderr)
    status, headers, body = get_crawl_status(job_id, format_json=False, retain_images=retain_images)
    
    if status == 200:
        content = body.decode("utf-8")
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Crawl results saved to: {output_file}", file=sys.stderr)
        else:
            sys.stdout.write(content)
    else:
        print(f"Failed to download crawl results. HTTP Status: {status}", file=sys.stderr)
        sys.exit(1)

def run_search(query, limit=3, gl="us", hl="en", retain_images=False, output_file=None, raw=False):
    """
    进行网页搜索，并提取出合并的 Markdown。
    """
    print_safety_warning()
    print(f"Searching for query: '{query}' (limit: {limit}, gl: {gl}, hl: {hl})...", file=sys.stderr)
    payload = {
        "q": query,
        "n": int(limit),
        "gl": gl,
        "hl": hl,
        "retain_images": retain_images
    }
    
    status, headers, body = request_api("/search", data=payload, method="POST")
    if status == 200:
        content = body.decode("utf-8")
        if not raw:
            try:
                js = json.loads(content)
                if isinstance(js, dict) and "combined" in js:
                    content = js["combined"]
            except Exception:
                pass

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Search results saved to: {output_file}", file=sys.stderr)
        else:
            sys.stdout.write(content)
    else:
        print(f"Failed to perform search. HTTP Status: {status}", file=sys.stderr)
        try:
            print(f"Response: {body.decode('utf-8')}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)

def main():
    epilog_text = (
        "安全与隐私警示:\n"
        "  1. 第三方中间商风险:\n"
        "     该工具请求需要通过第三方服务 (markdown.new)，这意味着被转换的网页内容或上传的文件均会发送至外部服务商处理。\n"
        "     严禁使用本工具转换任何商业机密、个人隐私或包含敏感凭证的内容。\n"
        "  2. 数据注入 (Prompt Injection) 风险:\n"
        "     由于中间服务商拥有改写并返回内容的控制权，将转换后的 Markdown 提供给大模型之前，请注意防范可能存在的恶意注入指令或欺骗性广告。"
    )
    parser = argparse.ArgumentParser(
        description="markdown.new API 命令行工具，提供网页转换、本地文档转换、整站爬取、全网搜索等多种 Markdown 导出功能。",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令 (convert | crawl | search)")
    
    # ------------------ convert parser ------------------
    convert_parser = subparsers.add_parser("convert", help="将指定网页 URL 或本地文件转换为 clean Markdown")
    convert_parser.add_argument("--url", help="要转换的目标网页 URL")
    convert_parser.add_argument("--file", help="要上传转换的本地文件路径（例如 PDF、Docx、Txt 等）")
    convert_parser.add_argument("--method", choices=["auto", "ai", "browser"], default="auto", 
                                 help="单页面提取策略：auto (默认，自动降级选择最佳方式), ai (AI智能解析), browser (动态浏览器渲染)")
    convert_parser.add_argument("--retain-images", action="store_true", help="是否在 Markdown 中保留 ![]() 图片链接 (默认剔除)")
    convert_parser.add_argument("--raw", action="store_true", help="输出接口返回的原始包含各项元数据的 JSON 信息，不自动提取 content 内容")
    convert_parser.add_argument("-o", "--output", help="输出的文件路径 (若未指定则直接输出到控制台 stdout)")
    
    # ------------------ crawl parser ------------------
    crawl_parser = subparsers.add_parser("crawl", help="爬取并合并整站多级目录网页为单个合并的 Markdown")
    crawl_parser.add_argument("--url", required=True, help="起始网站的入口 URL")
    crawl_parser.add_argument("--limit", type=int, default=500, help="最多抓取的网页页数限制 (范围 1-500，默认 500)")
    crawl_parser.add_argument("--depth", type=int, default=5, help="入口 URL 向下跳转的最大链接层级限制 (范围 1-10，默认 5)")
    crawl_parser.add_argument("--render", action="store_true", help="是否启用 JavaScript 动态浏览器渲染，用于爬取 SPA 单页应用 (默认 False)")
    crawl_parser.add_argument("--source", choices=["all", "sitemaps", "links"], default="all",
                               help="URL 发现的链接来源：all (默认), sitemaps (仅解析网站地图), links (仅解析页面中的超链接)")
    crawl_parser.add_argument("--max-age", type=int, default=86400, help="最大缓存更新时间，单位：秒 (范围 0-604800，默认 86400)")
    crawl_parser.add_argument("--modified-since", type=int, help="Unix 时间戳过滤：只爬取该时间戳之后修改的网页")
    crawl_parser.add_argument("--include-external-links", action="store_true", help="爬虫是否允许跟随链接进入并爬取外部其他域名 (默认 False)")
    crawl_parser.add_argument("--include-subdomains", action="store_true", help="爬虫是否允许抓取主域名下的各个子域名 (默认 False)")
    crawl_parser.add_argument("--include-patterns", help="只允许抓取符合这些通配符模式的 URL (以逗号分隔)")
    crawl_parser.add_argument("--exclude-patterns", help="排除并跳过符合这些通配符模式的 URL (以逗号分隔)")
    crawl_parser.add_argument("--retain-images", action="store_true", help="合并下载的 Markdown 中是否保留 ![]() 图片链接 (默认剔除)")
    crawl_parser.add_argument("-o", "--output", help="输出的合并 Markdown 文件路径 (若未指定则直接输出到控制台 stdout)")
    
    # ------------------ search parser ------------------
    search_parser = subparsers.add_parser("search", help="使用 Google 搜索并快速抓取排名前列的页面并合并转换为 Markdown")
    search_parser.add_argument("--query", required=True, help="搜索关键词")
    search_parser.add_argument("--limit", type=int, default=3, help="抓取排名前几的搜索页面并合并 (范围 1-5，默认 3)")
    search_parser.add_argument("--gl", default="us", help="谷歌搜索返回结果对应的 Geo-location 地区缩写 (例如 us, uk, cn, 默认 us)")
    search_parser.add_argument("--hl", default="en", help="搜索页面的 UI 界面展示语言 (例如 en, zh-cn, 默认 en)")
    search_parser.add_argument("--retain-images", action="store_true", help="合并后的搜索 Markdown 中是否保留 ![]() 图片链接 (默认剔除)")
    search_parser.add_argument("--raw", action="store_true", help="输出接口返回的原始 JSON 信息（包括每条结果的元数据），不提取 combined 字段")
    search_parser.add_argument("-o", "--output", help="输出的合并 Markdown 文件路径 (若未指定则直接输出到控制台 stdout)")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        if args.url and args.file:
            print("Error: Please specify either --url or --file, not both.", file=sys.stderr)
            sys.exit(1)
        elif args.url:
            convert_url(url=args.url, convert_method=args.method, retain_images=args.retain_images, 
                        output_file=args.output, raw=args.raw)
        elif args.file:
            convert_file(file_path=args.file, output_file=args.output)
        else:
            print("Error: Must specify --url or --file.", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "crawl":
        run_crawl(url=args.url, limit=args.limit, depth=args.depth, render=args.render, 
                  source=args.source, max_age=args.max_age, modified_since=args.modified_since,
                  include_external_links=args.include_external_links, include_subdomains=args.include_subdomains,
                  include_patterns=args.include_patterns, exclude_patterns=args.exclude_patterns,
                  retain_images=args.retain_images, output_file=args.output)
        
    elif args.command == "search":
        run_search(query=args.query, limit=args.limit, gl=args.gl, hl=args.hl, 
                   retain_images=args.retain_images, output_file=args.output, raw=args.raw)
        
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
