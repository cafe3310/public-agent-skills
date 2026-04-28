# 工作流：线上素材自动化收集与归档

## 目的
实现从 Obsidian 待办列表到本地素材库的自动化闭环处理。

## 准备工作
1.  确保已安装 `yt-dlp`, `pandoc`, `ffmpeg` 等核心工具。
2.  在 Obsidian 库中准备好以下三个 Markdown 文件：
    - `待本地化素材链接库.md` (输入)
    - `已经本地化素材.md` (成功记录)
    - `需要手动处理.md` (失败记录)

## 处理步骤

### 1. 任务读取与解析
*   读取 `待本地化素材链接库.md`。
*   **解析规则**:
    - 识别以 `http` 或 `https` 开头的行。
    - 记录该行及后续非链接行（备注）作为一个处理单元。
    - **示例**:
      ```markdown
      https://www.youtube.com/watch?v=xxx
      # 这是关于模型分镜的极佳参考
      ```

### 2. 智能分类下载
根据 URL 域名选择最佳工具：

*   **视频站点 (YouTube, Twitter, Bilibili等)**:
    - 调用 `yt-dlp`。
    - 命令示例: `yt-dlp --embed-metadata --embed-thumbnail -o "%(upload_date)s_%(uploader)s_%(title)s.%(ext)s" [URL]`
*   **内容站点 (博客, 知乎, Medium等)**:
    - 调用 `Pandoc` 或 `MarkItDown`。
    - 导出为 Markdown，并使用 `--embed-resources` 确保图片 Base64 嵌入。
*   **通用网页**:
    - 调用 `SingleFile` 保存为 HTML。

### 3. 存储与归档
*   将下载的文件存入 Obsidian 库下的 `Archive/Resources/{YYYYMMDD}/` 目录。
*   如果是 Markdown 文件，在 YAML Frontmatter 中注入：
    ```yaml
    source: [URL]
    notes: [用户备注]
    collected_at: [当前时间]
    ```

### 4. 状态同步 (Obsidian 联动)
*   **成功**:
    - 将该处理单元追加到 `已经本地化素材.md`。
    - 在 `待本地化素材链接库.md` 中删除对应内容。
*   **失败**:
    - 将该处理单元追加到 `需要手动处理.md`。
    - 在末尾附上错误日志摘要（如 `[Error] 403 Forbidden`）。

## 异常处理
*   **Cookie 失败**: 如果遇到登录限制，提示用户更新 `cookies.txt`。
*   **超时**: 自动重试 3 次，若仍失败则标记为“需要手动处理”。
