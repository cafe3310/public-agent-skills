const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8000;
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.mp4': 'video/mp4',
  '.mov': 'video/quicktime',
  '.webm': 'video/webm'
};

const IMG_EXTS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']);
const VID_EXTS = new Set(['.mp4', '.mov', '.webm', '.m4v']);

function parseFrontmatter(content) {
  const frontmatter = {};
  let body = content;
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  if (match) {
    const yamlText = match[1];
    body = content.slice(match[0].length);
    yamlText.split('\n').forEach(line => {
      const idx = line.indexOf(':');
      if (idx !== -1) {
        const key = line.slice(0, idx).trim();
        const val = line.slice(idx + 1).trim();
        frontmatter[key] = val;
      }
    });
  }
  return { frontmatter, body };
}

function generateData() {
  const baseDir = __dirname;
  const data = [];
  
  try {
    const items = fs.readdirSync(baseDir);
    
    items.forEach(item => {
      const itemPath = path.join(baseDir, item);
      if (!fs.statSync(itemPath).isDirectory()) return;
      
      const dirMatch = item.match(/^\[(\d{4}-\d{2}-\d{2}-\d{2})\]\s+([^\s]+)\s+(.+)$/);
      let dateStr = "";
      let category = "其他";
      let itemId = item;
      
      if (dirMatch) {
        dateStr = dirMatch[1];
        category = dirMatch[2];
        itemId = dirMatch[3];
      } else {
        if (!item.startsWith('[')) return;
      }
      
      const files = fs.readdirSync(itemPath);
      let mdFile = null;
      let jsonFile = null;
      const images = [];
      const videos = [];
      
      files.forEach(file => {
        const filePath = path.join(itemPath, file);
        if (fs.statSync(filePath).isDirectory()) return;
        
        const ext = path.extname(file).toLowerCase();
        if (ext === '.md') {
          if (file.startsWith(item) || !mdFile) {
            mdFile = file;
          }
        } else if (ext === '.json' && file === 'metadata.info.json') {
          jsonFile = file;
        } else if (IMG_EXTS.has(ext)) {
          images.push(file);
        } else if (VID_EXTS.has(ext)) {
          videos.push(file);
        }
      });
      
      images.sort();
      videos.sort();
      
      if (videos.length > 0 && images.length === 0) {
        const primaryVideo = videos[0];
        const videoPath = path.join(itemPath, primaryVideo);
        const thumbnailName = 'thumbnail.jpg';
        const thumbnailPath = path.join(itemPath, thumbnailName);
        
        try {
          const { spawnSync } = require('child_process');
          
          let duration = 0;
          const ffprobeResult = spawnSync('ffprobe', [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            videoPath
          ]);
          if (ffprobeResult.status === 0) {
            duration = parseFloat(ffprobeResult.stdout.toString().trim()) || 0;
          }
          
          const ssTime = Math.max(0, duration / 3).toFixed(3);
          console.log(`[Thumbnail Engine] 正在为仅有视频的目录生成缩略图 (SS: ${ssTime}s): ${item}`);
          
          const ffmpegResult = spawnSync('ffmpeg', [
            '-y',
            '-i', videoPath,
            '-ss', ssTime,
            '-vf', "scale='min(640,iw)':-1",
            '-strict', '-2',
            '-frames:v', '1',
            thumbnailPath
          ]);
          
          if (ffmpegResult.status === 0 && fs.existsSync(thumbnailPath)) {
            console.log(`[Thumbnail Engine] 成功生成缩略图: ${item} -> ${thumbnailName}`);
            images.push(thumbnailName);
          } else {
            console.warn(`[Thumbnail Engine] ffmpeg 运行失败或未生成文件: ${item}`);
          }
        } catch (err) {
          console.error(`[Thumbnail Engine] 调用 ffmpeg 发生异常 ${item}:`, err);
        }
      }
      
      let title = item;
      let sourceUrl = "";
      let collectedAt = "";
      let description = "";
      
      if (mdFile) {
        try {
          const content = fs.readFileSync(path.join(itemPath, mdFile), 'utf-8');
          const { frontmatter, body } = parseFrontmatter(content);
          
          title = frontmatter.title || title;
          sourceUrl = frontmatter.source || "";
          collectedAt = frontmatter.collected_at || "";
          
          let cleanBody = body.replace(/!\[\[.*?\]\]/g, '');
          cleanBody = cleanBody.replace(/^#\s+.*?\n/, '');
          cleanBody = cleanBody.replace(/## Metadata[\s\S]*/, '');
          description = cleanBody.trim();
        } catch (e) {
          console.error(`Error reading markdown in ${item}:`, e);
        }
      }
      
      let uploader = "";
      let likeCount = null;
      let repostCount = null;
      let duration = null;
      
      if (jsonFile) {
        try {
          const meta = JSON.parse(fs.readFileSync(path.join(itemPath, jsonFile), 'utf-8'));
          uploader = meta.uploader || "";
          if (!sourceUrl) sourceUrl = meta.webpage_url || "";
          if (!description) description = meta.description || "";
          likeCount = meta.like_count || null;
          repostCount = meta.repost_count || null;
          duration = meta.duration || null;
        } catch (e) {
          console.error(`Error reading JSON in ${item}:`, e);
        }
      }
      
      const encodedItem = encodeURIComponent(item);
      const mediaItems = [];
      
      videos.forEach(vid => {
        mediaItems.push({
          type: 'video',
          path: `${encodedItem}/${encodeURIComponent(vid)}`
        });
      });
      
      images.forEach(img => {
        mediaItems.push({
          type: 'image',
          path: `${encodedItem}/${encodeURIComponent(img)}`
        });
      });
      
      data.push({
        id: itemId,
        folderName: item,
        title,
        category,
        date: dateStr,
        sourceUrl,
        collectedAt,
        description,
        uploader,
        likeCount,
        repostCount,
        duration,
        media: mediaItems
      });
    });
    
    data.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    
    const outputContent = `// Auto-generated data file. Do not edit manually.\nwindow.COLLECTED_DATA = ${JSON.stringify(data, null, 2)};\n`;
    fs.writeFileSync(path.join(baseDir, 'data.js'), outputContent, 'utf-8');
    console.log(`[Data Sync] 成功同步了 ${data.length} 个收藏项目。`);
  } catch (e) {
    console.error("生成数据文件时发生错误:", e);
  }
}

generateData();

const server = http.createServer((req, res) => {
  const urlPath = req.url.split('?')[0];
  
  if (urlPath === '/data.js') {
    generateData();
  }
  
  let filePath = path.join(__dirname, decodeURIComponent(urlPath));
  
  if (urlPath === '/' || urlPath === '') {
    filePath = path.join(__dirname, 'index.html');
  }
  
  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found - 找不到请求的文件');
      return;
    }
    
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    
    const range = req.headers.range;
    if (range && (ext === '.mp4' || ext === '.mov' || ext === '.webm')) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stats.size - 1;
      const chunksize = (end - start) + 1;
      
      const file = fs.createReadStream(filePath, { start, end });
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stats.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': contentType
      });
      file.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': stats.size,
        'Content-Type': contentType
      });
      fs.createReadStream(filePath).pipe(res);
    }
  });
});

server.listen(PORT, () => {
  console.log(`==================================================`);
  console.log(`  网络收藏看版静态服务器已在 Node.js 中启动`);
  console.log(`  请在浏览器中打开: http://localhost:${PORT}`);
  console.log(`  按 Ctrl + C 可以停止服务器`);
  console.log(`==================================================`);
});
