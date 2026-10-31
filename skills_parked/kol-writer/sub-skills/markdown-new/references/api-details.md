# markdown.new API 详细参考与排查指南

本指南详细记录了 `markdown.new` 转换服务的管道设计、API 参数细则及异常处理方法，旨在帮助 Agent 或开发者更好地在开发和运行时使用本技能。

---

## 一、三级转换管道设计

`markdown.new` 会自动按照响应速度和效果对每个 URL 执行三阶段降级（Fallback）请求：
1. **Tier 1 (Accept header 协商)**：带上 `Accept: text/markdown` 请求目标 URL。如果站点在 Cloudflare 网络上并开启了“Markdown for Agents”，则直接由边缘节点无感返回转换好的 Markdown，没有任何计算开销。
2. **Tier 2 (Workers AI `toMarkdown()`)**：如果第一步协商返回了 HTML 页面，Cloudflare 会调用 Workers AI 的 `toMarkdown()` 方法将 HTML 直接原地转换为 Markdown，不需要二次请求。
3. **Tier 3 (Browser Rendering API)**：对于由 JavaScript 重度渲染的页面，Cloudflare 会在后台拉起无头浏览器（Headless Browser）进行完整页面渲染，并抓取转换。

---

## 二、详细参数参考

### 1. `convert` 模式 (页面与文件转换)
- **单网页 API 传参 (`POST /`)**
  - `url` (String, 必填): 目标网页 URL。
  - `method` (String, 默认 `auto`): 单页抓取策略。支持 `auto`（自动降级选择）、`ai`（AI 智能解析转换）、`browser`（动态浏览器渲染，用于 JS-heavy 网站）。
  - `retain_images` (Boolean, 默认 `false`): 是否在输出中保留图片。
- **本地文件 API 传参 (`POST /convert`)**
  - `file` (Binary, 必填): 上传本地 PDF、Docx、Txt 等文档文件，服务将返回其对应的 Markdown 文本。

### 2. `crawl` 模式 (整站/目录爬取)
- **启动爬虫 API 传参 (`POST /crawl`)**
  - `url` (String, 必填): 入口 URL。
  - `limit` (Int, 默认 `500`): 爬取页面最大限制，范围 1–500。
  - `depth` (Int, 默认 `5`): 入口往下最深跳转层数，范围 1–10。
  - `render` (Boolean, 默认 `false`): 开启 JS 渲染。
  - `source` (String, 默认 `all`): URL 链接发现源。支持 `all`、`sitemaps` (仅从站点地图提取) 或 `links` (从页面超链接发现)。
  - `maxAge` (Int, 默认 `86400`): 缓存秒数，默认 1 天。
  - `modifiedSince` (Int): 过滤仅爬取此时间戳后有更新的页面。
  - `includeExternalLinks` (Boolean, 默认 `false`): 跟随链接爬取外部域名。
  - `includeSubdomains` (Boolean, 默认 `false`): 允许抓取子域名下的网页。
  - `includePatterns` (Array): 通配符匹配访问路径模式。
  - `excludePatterns` (Array): 通配符排除访问路径模式。
- **获取状态及下载 (`GET /crawl/status/:jobId`)**
  - 默认返回已合并的 Markdown 文本；可在 Status 路径拼上 `&retain_images=true` 以使最终的 Markdown 保留图片。
  - 拼接 `?format=json` 获取包含爬取进度、各页面元数据和状态的 structured JSON 封包。
  - 缓存机制：爬取结果在 Cloudflare 会**保存 14 天**，过期将被物理删除。

### 3. `search` 模式 (网页搜索合并)
- **搜索 API 传参 (`POST /search`)**
  - `q` (String, 必填): 搜索关键词。
  - `n` (Int, 默认 `3`): 返回的最佳 organic 搜索结果提取页数，范围 1–5。
  - `gl` (String, 默认 `us`): 地理定位编码 (如 us, cn, de, uk)。
  - `hl` (String, 默认 `en`): 搜索界面 UI 展示语言。
  - `retain_images` (Boolean, 默认 `false`): 提取出的 Markdown 是否包含图片链接。

---

## 三、限制与额度 (Rate Limits)

1. **基本转换限制**：
   - 每日最大转换量：每个 IP 地址 **500 次/天**。
   - 返回 429 频率限制时，需要等待次日重置。
2. **爬虫 (Crawl) 限制**：
   - 单次 Crawl 消耗 50 个请求额度。
   - 每个 IP 每天大约只能发起 **10 次完整的 Crawl 任务**（500 额度 ÷ 50）。
3. **网页搜索 (Search) 限制**：
   - 每分钟最高请求数：**30 次/分钟**。
   - 每天最大搜索数：每个 IP 地址 **500 次/天**。
   - 全球共享总硬上限：所有使用者每天最高共计 **60,000 次** 搜索请求。

---

## 四、异常排查与应对建议

| 异常表现 | 可能原因 | 应对方案 |
| :--- | :--- | :--- |
| **HTTP 429** | 当前 IP 请求超过了每天 500 次的限制，或者搜索请求超过了 30 次/分钟的频控。 | 1. 降低并发频率。<br>2. 等待次日限额重置。<br>3. 对于拥有大量流量的项目，应考虑通过 Cloudflare 进行本地自建 / self-hosting。 |
| **HTTP 401 / 403** | 目标网页设置了 Cloudflare WAF 强防护、人机验证（CAPTCHA）或需要授权访问的支付墙。 | `markdown.new` 仅针对公开 URL 生效。若页面受强安全保护或存在登录验证，应当放弃代理请求，降级为使用本地浏览器、MCP 浏览器服务，或使用本地爬虫拉取内容。 |
| **HTTP 504 (Gateway Timeout)** | `method=browser` 针对重度 JS 页面加载速度慢，或目标 origin 响应超时（由于单页在边缘服务器下载限制不能超过 2MB 且需在 10s 内返回）。 | 1. 尝试降级使用 `method=auto` 或 `method=ai`。<br>2. 检查源站是否能正常访问并保证 origin 包大小在 2MB 以内。 |
| **Crawl 任务一直处于 Pending/Failed** | 被爬取的目标网站在 `robots.txt` 中显式封禁了爬虫标识 `User-agent: markdown.new`。 | 遵守目标网站的 `robots.txt` 规则。如为个人合法需要，可采用本地脚本解析。 |
