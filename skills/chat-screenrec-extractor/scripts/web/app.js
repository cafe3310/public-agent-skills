// Chat Screenrec Extractor - Calibration Web UI App

const state = {
  videos: [],
  selectedVideo: null,
  videoMeta: { duration: 0, width: 0, height: 0, fps: 30 },
  currentTime: 0.0,
  interval: 0.8,
  activeMode: 'title', // 'title' | 'body'
  
  // Normalized ROIs (0..1)
  // Default sensible phone screen bounds
  titleROI: { x: 0.0, y: 0.04, w: 1.0, h: 0.08 },
  bodyROI: { x: 0.0, y: 0.12, w: 1.0, h: 0.78 },
  
  isDragging: false,
  dragStart: { x: 0, y: 0 },
  currentDrag: { x: 0, y: 0 },
  
  currentImage: null,
  isLoadingFrame: false
};

// DOM Elements
const videoSelect = document.getElementById('video-select');
const videoMeta = document.getElementById('video-meta');
const intervalSlider = document.getElementById('interval-slider');
const intervalVal = document.getElementById('interval-val');
const frameEstimate = document.getElementById('frame-estimate');
const timelineSlider = document.getElementById('timeline-slider');
const currentTimeDisplay = document.getElementById('current-time');
const totalTimeDisplay = document.getElementById('total-time');
const prevFrameBtn = document.getElementById('prev-frame-btn');
const nextFrameBtn = document.getElementById('next-frame-btn');
const modeTitleBtn = document.getElementById('mode-title-btn');
const modeBodyBtn = document.getElementById('mode-body-btn');
const resetRoiBtn = document.getElementById('reset-roi-btn');
const applyPresetBtn = document.getElementById('apply-preset-btn');
const titleCoords = document.getElementById('title-coords');
const bodyCoords = document.getElementById('body-coords');
const saveConfigBtn = document.getElementById('save-config-btn');
const statusBadge = document.getElementById('status-badge');
const loadingOverlay = document.getElementById('loading-overlay');
const toast = document.getElementById('toast');

const mainCanvas = document.getElementById('main-canvas');
const ctx = mainCanvas.getContext('2d');

const titleCropCanvas = document.getElementById('title-crop-canvas');
const titleCropCtx = titleCropCanvas.getContext('2d');

const bodyCropCanvas = document.getElementById('body-crop-canvas');
const bodyCropCtx = bodyCropCanvas.getContext('2d');

// Helper: Format seconds to MM:SS.m
function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  const ms = Math.floor((sec % 1) * 10);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${ms}`;
}

// Show Toast
function showToast(msg, duration = 3000) {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// Initialize Application
async function init() {
  setupEventListeners();
  await loadVideoList();
}

// Load Video List from backend
async function loadVideoList() {
  try {
    const res = await fetch('/api/videos');
    const data = await res.json();
    state.videos = data.videos || [];
    
    videoSelect.innerHTML = '';
    if (state.videos.length === 0) {
      videoSelect.innerHTML = '<option value="">未在当前目录检测到视频文件</option>';
      statusBadge.textContent = '无视频';
      return;
    }
    
    state.videos.forEach((v, idx) => {
      const opt = document.createElement('option');
      opt.value = v.rel_path;
      opt.textContent = `${v.name} (${(v.size / (1024*1024)).toFixed(1)} MB)`;
      videoSelect.appendChild(opt);
    });

    // If config was saved before, restore it
    if (data.saved_config) {
      const cfg = data.saved_config;
      if (cfg.interval_seconds) {
        state.interval = cfg.interval_seconds;
        intervalSlider.value = cfg.interval_seconds;
        intervalVal.textContent = `${cfg.interval_seconds}s`;
      }
      if (cfg.title_roi) state.titleROI = cfg.title_roi;
      if (cfg.body_roi) state.bodyROI = cfg.body_roi;
      updateReadouts();
    }

    // Select first video
    if (state.videos.length > 0) {
      await selectVideo(state.videos[0].rel_path);
    }
  } catch (err) {
    console.error('Failed to load videos:', err);
    showToast('加载视频列表失败');
  }
}

// Select and load video info
async function selectVideo(relPath) {
  state.selectedVideo = relPath;
  videoSelect.value = relPath;
  state.currentTime = 0.0;
  timelineSlider.value = 0;

  try {
    const res = await fetch(`/api/video_info?video=${encodeURIComponent(relPath)}`);
    const info = await res.json();
    state.videoMeta = info;
    
    videoMeta.textContent = `分辨率: ${info.width}x${info.height} | 时长: ${formatTime(info.duration)} | 帧率: ${info.fps}fps`;
    totalTimeDisplay.textContent = formatTime(info.duration);
    timelineSlider.max = info.duration > 0 ? info.duration : 100;
    
    updateEstimate();
    await loadFrame(state.currentTime);
  } catch (err) {
    console.error('Failed to get video info:', err);
  }
}

function updateEstimate() {
  if (state.videoMeta.duration > 0 && state.interval > 0) {
    const est = Math.ceil(state.videoMeta.duration / state.interval);
    frameEstimate.textContent = `预计单视频抽帧: ~${est} 张图片`;
    prevFrameBtn.textContent = `⏪ 上一帧 (-${state.interval}s)`;
    nextFrameBtn.textContent = `⏩ 下一帧 (+${state.interval}s)`;
  }
}

// Load Frame Image from Server
async function loadFrame(timestamp) {
  if (!state.selectedVideo) return;
  state.currentTime = Math.max(0, Math.min(timestamp, state.videoMeta.duration || 100));
  currentTimeDisplay.textContent = formatTime(state.currentTime);
  timelineSlider.value = state.currentTime;

  loadingOverlay.style.display = 'flex';
  state.isLoadingFrame = true;

  const url = `/api/frame?video=${encodeURIComponent(state.selectedVideo)}&time=${state.currentTime.toFixed(3)}`;
  const img = new Image();
  img.onload = () => {
    state.currentImage = img;
    state.isLoadingFrame = false;
    loadingOverlay.style.display = 'none';
    renderCanvas();
    renderCrops();
  };
  img.onerror = () => {
    state.isLoadingFrame = false;
    loadingOverlay.style.display = 'none';
    showToast('提取当前帧失败');
  };
  img.src = url;
}

// Render Main Canvas with Frame and ROI Boxes
function renderCanvas() {
  if (!state.currentImage) return;
  const img = state.currentImage;
  
  mainCanvas.width = img.naturalWidth || 1080;
  mainCanvas.height = img.naturalHeight || 2400;

  // Draw background frame
  ctx.drawImage(img, 0, 0, mainCanvas.width, mainCanvas.height);

  const W = mainCanvas.width;
  const H = mainCanvas.height;

  // 1. Draw Title ROI (Red)
  if (state.titleROI) {
    const rx = state.titleROI.x * W;
    const ry = state.titleROI.y * H;
    const rw = state.titleROI.w * W;
    const rh = state.titleROI.h * H;

    ctx.fillStyle = 'rgba(255, 92, 92, 0.25)';
    ctx.fillRect(rx, ry, rw, rh);
    ctx.strokeStyle = '#ff5c5c';
    ctx.lineWidth = Math.max(2, Math.floor(W / 400));
    ctx.strokeRect(rx, ry, rw, rh);

    // Label tag
    ctx.fillStyle = '#ff5c5c';
    const tagH = Math.max(18, Math.floor(H / 80));
    ctx.fillRect(rx, ry, Math.min(rw, 140), tagH);
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${tagH - 4}px sans-serif`;
    ctx.fillText('群聊标题栏 (Title)', rx + 6, ry + tagH - 4);
  }

  // 2. Draw Body ROI (Blue)
  if (state.bodyROI) {
    const rx = state.bodyROI.x * W;
    const ry = state.bodyROI.y * H;
    const rw = state.bodyROI.w * W;
    const rh = state.bodyROI.h * H;

    ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
    ctx.fillRect(rx, ry, rw, rh);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = Math.max(2, Math.floor(W / 400));
    ctx.strokeRect(rx, ry, rw, rh);

    // Label tag
    ctx.fillStyle = '#3b82f6';
    const tagH = Math.max(18, Math.floor(H / 80));
    ctx.fillRect(rx, ry, Math.min(rw, 140), tagH);
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${tagH - 4}px sans-serif`;
    ctx.fillText('消息记录区 (Body)', rx + 6, ry + tagH - 4);
  }

  // 3. Draw Active Dragging Box
  if (state.isDragging) {
    const x1 = Math.min(state.dragStart.x, state.currentDrag.x) * W;
    const y1 = Math.min(state.dragStart.y, state.currentDrag.y) * H;
    const bw = Math.abs(state.currentDrag.x - state.dragStart.x) * W;
    const bh = Math.abs(state.currentDrag.y - state.dragStart.y) * H;

    ctx.setLineDash([6, 4]);
    if (state.activeMode === 'title') {
      ctx.fillStyle = 'rgba(255, 92, 92, 0.4)';
      ctx.strokeStyle = '#ffffff';
    } else {
      ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
      ctx.strokeStyle = '#ffffff';
    }
    ctx.fillRect(x1, y1, bw, bh);
    ctx.strokeRect(x1, y1, bw, bh);
    ctx.setLineDash([]);
  }
}

// Render Side Previews for Title and Body crops
function renderCrops() {
  if (!state.currentImage) return;
  const img = state.currentImage;
  const W = img.naturalWidth;
  const H = img.naturalHeight;

  // Title Crop
  if (state.titleROI && state.titleROI.w > 0 && state.titleROI.h > 0) {
    const sx = Math.max(0, state.titleROI.x * W);
    const sy = Math.max(0, state.titleROI.y * H);
    const sw = Math.min(W - sx, state.titleROI.w * W);
    const sh = Math.min(H - sy, state.titleROI.h * H);

    titleCropCanvas.width = sw;
    titleCropCanvas.height = sh;
    titleCropCtx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);
  }

  // Body Crop
  if (state.bodyROI && state.bodyROI.w > 0 && state.bodyROI.h > 0) {
    const sx = Math.max(0, state.bodyROI.x * W);
    const sy = Math.max(0, state.bodyROI.y * H);
    const sw = Math.min(W - sx, state.bodyROI.w * W);
    const sh = Math.min(H - sy, state.bodyROI.h * H);

    bodyCropCanvas.width = sw;
    bodyCropCanvas.height = sh;
    bodyCropCtx.drawImage(img, sx, sy, sw, sh, 0, 0, sw, sh);
  }
}

// Update text readouts
function updateReadouts() {
  if (state.titleROI) {
    const r = state.titleROI;
    titleCoords.textContent = `x:${(r.x*100).toFixed(1)}% y:${(r.y*100).toFixed(1)}% w:${(r.w*100).toFixed(1)}% h:${(r.h*100).toFixed(1)}%`;
  } else {
    titleCoords.textContent = '未设置';
  }

  if (state.bodyROI) {
    const r = state.bodyROI;
    bodyCoords.textContent = `x:${(r.x*100).toFixed(1)}% y:${(r.y*100).toFixed(1)}% w:${(r.w*100).toFixed(1)}% h:${(r.h*100).toFixed(1)}%`;
  } else {
    bodyCoords.textContent = '未设置';
  }
}

// Convert Mouse/Touch Event to Normalized Canvas Coords (0..1)
function getNormalizedCoords(e) {
  const rect = mainCanvas.getBoundingClientRect();
  const clientX = e.clientX || (e.touches && e.touches[0].clientX);
  const clientY = e.clientY || (e.touches && e.touches[0].clientY);
  
  const normX = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
  const normY = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));
  return { x: normX, y: normY };
}

// Setup Event Listeners
function setupEventListeners() {
  // Video select
  videoSelect.addEventListener('change', (e) => {
    if (e.target.value) selectVideo(e.target.value);
  });

  // Interval slider
  intervalSlider.addEventListener('input', (e) => {
    state.interval = parseFloat(e.target.value);
    intervalVal.textContent = `${state.interval.toFixed(1)}s`;
    updateEstimate();
  });

  // Timeline slider
  timelineSlider.addEventListener('input', (e) => {
    const t = parseFloat(e.target.value);
    loadFrame(t);
  });

  // Prev / Next Frame
  prevFrameBtn.addEventListener('click', () => {
    loadFrame(state.currentTime - state.interval);
  });
  nextFrameBtn.addEventListener('click', () => {
    loadFrame(state.currentTime + state.interval);
  });

  // Mode Buttons
  modeTitleBtn.addEventListener('click', () => {
    state.activeMode = 'title';
    modeTitleBtn.classList.add('active');
    modeBodyBtn.classList.remove('active');
  });
  modeBodyBtn.addEventListener('click', () => {
    state.activeMode = 'body';
    modeBodyBtn.classList.add('active');
    modeTitleBtn.classList.remove('active');
  });

  // Reset ROI
  resetRoiBtn.addEventListener('click', () => {
    if (state.activeMode === 'title') {
      state.titleROI = null;
    } else {
      state.bodyROI = null;
    }
    updateReadouts();
    renderCanvas();
    renderCrops();
  });

  // Preset
  applyPresetBtn.addEventListener('click', () => {
    state.titleROI = { x: 0.0, y: 0.04, w: 1.0, h: 0.08 };
    state.bodyROI = { x: 0.0, y: 0.12, w: 1.0, h: 0.78 };
    updateReadouts();
    renderCanvas();
    renderCrops();
    showToast('已应用手机常用群聊界面预设');
  });

  // Canvas Mouse Events for Drag Box Selection
  mainCanvas.addEventListener('mousedown', (e) => {
    if (!state.currentImage) return;
    const pos = getNormalizedCoords(e);
    state.isDragging = true;
    state.dragStart = pos;
    state.currentDrag = pos;
  });

  window.addEventListener('mousemove', (e) => {
    if (!state.isDragging) return;
    state.currentDrag = getNormalizedCoords(e);
    renderCanvas();
  });

  window.addEventListener('mouseup', () => {
    if (!state.isDragging) return;
    state.isDragging = false;

    const x = Math.min(state.dragStart.x, state.currentDrag.x);
    const y = Math.min(state.dragStart.y, state.currentDrag.y);
    const w = Math.abs(state.currentDrag.x - state.dragStart.x);
    const h = Math.abs(state.currentDrag.y - state.dragStart.y);

    // Filter tiny unintentional clicks
    if (w > 0.02 && h > 0.01) {
      const roi = {
        x: Math.round(x * 1000) / 1000,
        y: Math.round(y * 1000) / 1000,
        w: Math.round(w * 1000) / 1000,
        h: Math.round(h * 1000) / 1000
      };

      if (state.activeMode === 'title') {
        state.titleROI = roi;
      } else {
        state.bodyROI = roi;
      }
    }

    updateReadouts();
    renderCanvas();
    renderCrops();
  });

  // Save Configuration
  saveConfigBtn.addEventListener('click', async () => {
    if (!state.titleROI || !state.bodyROI) {
      showToast('请先框选群聊标题栏与消息正文区');
      return;
    }

    const payload = {
      interval_seconds: state.interval,
      title_roi: state.titleROI,
      body_roi: state.bodyROI,
      calibrated_resolution: {
        width: state.videoMeta.width,
        height: state.videoMeta.height
      },
      updated_at: new Date().toISOString()
    };

    try {
      saveConfigBtn.disabled = true;
      saveConfigBtn.textContent = '保存中...';
      const res = await fetch('/api/save_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        statusBadge.textContent = '已保存配置';
        statusBadge.classList.add('success');
        showToast(`配置已保存至: ${data.saved_to}`);
      } else {
        showToast(`保存失败: ${data.error}`);
      }
    } catch (err) {
      showToast('保存请求出错');
    } finally {
      saveConfigBtn.disabled = false;
      saveConfigBtn.textContent = '💾 保存配置 (Save Config)';
    }
  });
}

// Start
window.addEventListener('DOMContentLoaded', init);
