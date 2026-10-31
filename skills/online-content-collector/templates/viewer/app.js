// app.js - Network Collection Viewer logic (Zed Industrial style)

document.addEventListener('DOMContentLoaded', () => {
  // If single page, add class to body to disable animations/transitions
  if (window.IS_SINGLE_PAGE) {
    document.body.classList.add('single-page');
  }

  // Check if data is available
  if (!window.COLLECTED_DATA) {
    console.error("COLLECTED_DATA not found. Please run the scanner script.");
    showEmptyState("未找到数据，请先运行数据扫描脚本 generate_data.py。");
    return;
  }

  const data = window.COLLECTED_DATA;
  
  // State variables
  let currentCategory = 'all';
  let searchQuery = '';
  let currentSort = 'date-desc';
  let currentLayout = 'grid'; // 'grid' or 'masonry'
  let displayedCount = 24;
  const pageIncrement = 24;
  
  // Modal State
  let activeItem = null;
  let activeMediaIndex = 0;

  // DOM Elements
  const cardsContainer = document.getElementById('cards-container');
  const searchInput = document.getElementById('search-input');
  const searchClear = document.getElementById('search-clear');
  const tagButtons = document.querySelectorAll('.tag-btn');
  const sortSelect = document.getElementById('sort-select');
  const layoutBtnGrid = document.getElementById('layout-grid');
  const layoutBtnMasonry = document.getElementById('layout-masonry');
  
  // Stats Elements
  const statTotal = document.getElementById('stat-total');
  const statVideos = document.getElementById('stat-videos');
  const statImages = document.getElementById('stat-images');
  
  // Modal Elements
  const modal = document.getElementById('detail-modal');
  const modalMediaSide = document.getElementById('modal-media-side');
  const modalContentSide = document.getElementById('modal-content-side');
  const modalCloseBtn = document.getElementById('modal-close');

  // Initialize statistics
  function updateStats() {
    let videoCount = 0;
    let imageCount = 0;
    
    data.forEach(item => {
      item.media.forEach(m => {
        if (m.type === 'video') videoCount++;
        else if (m.type === 'image') imageCount++;
      });
    });
    
    statTotal.innerHTML = `<strong>${data.length}</strong> 收藏`;
    statVideos.innerHTML = `<strong>${videoCount}</strong> 视频`;
    statImages.innerHTML = `<strong>${imageCount}</strong> 图片`;
  }

  // Generate static category tag filters (文字, 图片, 视频)
  function renderCategoryTags() {
    const filterWrapper = document.querySelector('.filter-tags-wrapper');
    filterWrapper.innerHTML = '';
    
    const categories = ['all', '文字', '图片', '视频'];
    categories.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = `tag-btn${cat === 'all' ? ' active' : ''}`;
      btn.setAttribute('data-category', cat);
      
      if (cat === 'all') {
        btn.innerHTML = `
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          全部
        `;
      } else {
        btn.textContent = cat;
      }
      
      btn.addEventListener('click', () => handleCategoryChange(cat, btn));
      filterWrapper.appendChild(btn);
    });
  }

  function handleCategoryChange(cat, clickedBtn) {
    currentCategory = cat;
    
    document.querySelectorAll('.filter-tags-wrapper .tag-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    if (clickedBtn) {
      clickedBtn.classList.add('active');
    }
    
    renderCards();
  }

  // Filter & Sort Data
  function getFilteredData() {
    let filtered = data.filter(item => {
      // Category filter
      if (currentCategory !== 'all' && item.category !== currentCategory) {
        return false;
      }
      
      // Search query filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const inTitle = item.title && item.title.toLowerCase().includes(query);
        const inDesc = item.description && item.description.toLowerCase().includes(query);
        const inUploader = item.uploader && item.uploader.toLowerCase().includes(query);
        const inCat = item.category && item.category.toLowerCase().includes(query);
        const inTags = item.tags && item.tags.some(t => t.toLowerCase().includes(query));
        return inTitle || inDesc || inUploader || inCat || inTags;
      }
      
      return true;
    });
    
    // Sorting
    if (currentSort === 'date-desc') {
      filtered.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    } else if (currentSort === 'date-asc') {
      filtered.sort((a, b) => (a.date || '').localeCompare(b.date || ''));
    } else if (currentSort === 'likes-desc') {
      filtered.sort((a, b) => (b.likeCount || 0) - (a.likeCount || 0));
    } else if (currentSort === 'random') {
      filtered.sort(() => Math.random() - 0.5);
    }
    
    return filtered;
  }

  // Build a single card element
  function createCard(item, index) {
    const card = document.createElement('div');
    card.className = 'card';
    card.setAttribute('data-id', item.id);
    
    // Render static block without video request on list page
    let mediaHtml = '';
    const hasMedia = item.media && item.media.length > 0;
    
    if (hasMedia) {
      const hasVideo = item.media.some(m => m.type === 'video');
      const imageMedia = item.media.find(m => m.type === 'image');
      const primaryMedia = imageMedia || item.media[0];
      const isVideo = primaryMedia.type === 'video';
      
      if (isVideo) {
        // Do not render <video> tag on list page - use high contrast static play button card
        mediaHtml = `
          <div class="card-media-wrapper">
            <div class="video-static-placeholder">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <span>[点击播放视频]</span>
            </div>
            <div class="media-indicator">视频</div>
          </div>
        `;
      } else {
        // It's an image. Show video badge if the item contains a video (so this image acts as a thumbnail)
        const videoIndicator = hasVideo ? `
          <div class="media-indicator">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="12" height="12" style="margin-right:2px; vertical-align:middle; display:inline-block;">
              <path d="M8 5v14l11-7z"/>
            </svg>
            视频
          </div>
        ` : '';
        
        const imageFilesCount = item.media.filter(m => m.type === 'image').length;
        const countIndicator = (!hasVideo && imageFilesCount > 1) ? `<div class="image-count-indicator">${imageFilesCount} 图</div>` : '';
        
        mediaHtml = `
          <div class="card-media-wrapper">
            <img class="card-media lazy-media" data-src="${primaryMedia.path}" alt="${item.title}">
            ${videoIndicator}
            ${countIndicator}
          </div>
        `;
      }
    } else {
      mediaHtml = `
        <div class="media-placeholder">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="9" cy="9" r="2"/>
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
          </svg>
          <span>[无媒体内容]</span>
        </div>
      `;
    }
    
    // Format interaction counts
    const likes = item.likeCount ? formatNumber(item.likeCount) : '';
    
    // Short date formatting
    const displayDate = item.date ? item.date.replace(/-(\d{2})$/, ' $1时') : '';
    
    let tagsHtml = '';
    if (item.tags && item.tags.length > 0) {
      tagsHtml = `
        <div class="card-tags-flow">
          ${item.tags.map(t => `<span class="card-tag-item">#${t}</span>`).join('')}
        </div>
      `;
    }
    
    card.innerHTML = `
      ${mediaHtml}
      <div class="card-body">
        <div class="card-meta-header">
          <span class="category-badge" data-category="${item.category}">${item.category}</span>
          <span class="card-date">${displayDate}</span>
        </div>
        <h3 class="card-title" title="${item.title}">${item.title}</h3>
        <p class="card-description">${item.description || '无正文描述'}</p>
        ${tagsHtml}
        <div class="card-footer">
          <div class="uploader-info">
            <span class="uploader-name" title="${item.uploader || '匿名'}">${item.uploader || '匿名'}</span>
          </div>
          <div class="card-actions">
            ${likes ? `
              <div class="action-stat" title="点赞数">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
                <span>${likes}</span>
              </div>
            ` : ''}
            ${item.sourceUrl ? `
              <a href="${item.sourceUrl}" target="_blank" class="source-link" title="查看原始链接" onclick="event.stopPropagation();">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            ` : ''}
          </div>
        </div>
      </div>
    `;
    
    // Add Click listener to open Modal details where the media actually loads
    card.addEventListener('click', () => openModal(item));
    
    return card;
  }

  // Render cards to container
  let lazyObserver = null;
  
  function renderCards(append = false) {
    const filtered = getFilteredData();
    
    if (!append) {
      cardsContainer.innerHTML = '';
      displayedCount = pageIncrement;
    }
    
    if (filtered.length === 0) {
      showEmptyState("没有找到匹配的收藏记录。");
      removeLoadMoreTrigger();
      return;
    }
    
    const sliceToRender = filtered.slice(append ? displayedCount - pageIncrement : 0, displayedCount);
    
    // Create Document Fragment for performance
    const fragment = document.createDocumentFragment();
    sliceToRender.forEach((item, index) => {
      const card = createCard(item, append ? index + pageIncrement : index);
      fragment.appendChild(card);
    });
    
    cardsContainer.appendChild(fragment);
    
    // Initialize or refresh lazy loading observer
    setupLazyLoading();
    
    // Setup infinite scroll trigger
    if (displayedCount < filtered.length) {
      setupLoadMoreTrigger();
    } else {
      removeLoadMoreTrigger();
    }
    
    if (typeof updateScrollIndicator === 'function') {
      updateScrollIndicator();
    }
  }

  // Lazy Loading Setup
  function setupLazyLoading() {
    if (lazyObserver) {
      lazyObserver.disconnect();
    }
    
    lazyObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const mediaEl = entry.target;
          const src = mediaEl.getAttribute('data-src');
          if (src) {
            mediaEl.src = src;
            mediaEl.removeAttribute('data-src');
            mediaEl.addEventListener('load', () => mediaEl.classList.add('loaded'));
          }
          observer.unobserve(mediaEl);
        }
      });
    }, { rootMargin: '200px 0px' });
    
    const lazyElements = cardsContainer.querySelectorAll('.lazy-media');
    lazyElements.forEach(el => lazyObserver.observe(el));
  }

  // Infinite scroll threshold trigger
  let loadMoreObserver = null;
  
  function setupLoadMoreTrigger() {
    removeLoadMoreTrigger();
    
    // Create trigger element if not exists
    let trigger = document.getElementById('load-more-trigger');
    if (!trigger) {
      trigger = document.createElement('div');
      trigger.id = 'load-more-trigger';
      trigger.className = 'loader';
      trigger.innerHTML = '<div class="spinner"></div>';
      cardsContainer.parentNode.appendChild(trigger);
    }
    
    loadMoreObserver = new IntersectionObserver((entries) => {
      const filtered = getFilteredData();
      if (entries[0].isIntersecting && displayedCount < filtered.length) {
        displayedCount += pageIncrement;
        renderCards(true);
      }
    }, { rootMargin: '100px' });
    
    loadMoreObserver.observe(trigger);
  }

  function removeLoadMoreTrigger() {
    if (loadMoreObserver) {
      loadMoreObserver.disconnect();
    }
    const trigger = document.getElementById('load-more-trigger');
    if (trigger) {
      trigger.remove();
    }
  }

  // Empty State Helper
  function showEmptyState(message) {
    cardsContainer.innerHTML = `
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>${message}</p>
      </div>
    `;
  }

  // Helpers
  function formatNumber(num) {
    if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num;
  }
  
  function urlify(text) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.replace(urlRegex, function(url) {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
  }

  // Handle category button click
  function handleCategoryChange(cat, clickedBtn) {
    currentCategory = cat;
    
    // Update active button classes
    document.querySelectorAll('.tag-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    if (clickedBtn) {
      clickedBtn.classList.add('active');
    } else {
      const match = document.querySelector(`.tag-btn[data-category="${cat}"]`);
      if (match) match.classList.add('active');
    }
    
    renderCards();
  }

  // Modal Open & Render
  function openModal(item) {
    activeItem = item;
    activeMediaIndex = 0;
    
    // Add overflow hidden to body
    document.body.style.overflow = 'hidden';
    
    if (!item.media || item.media.length === 0) {
      modal.classList.add('no-media-mode');
    } else {
      modal.classList.remove('no-media-mode');
    }
    
    modal.classList.add('open');
    
    renderModalMedia();
    renderModalContent();
    
    // Register keyboard listeners
    document.addEventListener('keydown', handleModalKeys);
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.classList.remove('no-media-mode');
    document.body.style.overflow = '';
    
    // Stop any playing video in modal
    const video = modalMediaSide.querySelector('video');
    if (video) video.pause();
    
    // Unregister keyboard listeners
    document.removeEventListener('keydown', handleModalKeys);
    activeItem = null;
  }

  function handleModalKeys(e) {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'ArrowRight' || e.key === 'Right') {
      navigateMedia(1);
    }
    if (e.key === 'ArrowLeft' || e.key === 'Left') {
      navigateMedia(-1);
    }
  }

  function navigateMedia(dir) {
    if (!activeItem || !activeItem.media || activeItem.media.length <= 1) return;
    
    activeMediaIndex = (activeMediaIndex + dir + activeItem.media.length) % activeItem.media.length;
    renderModalMedia();
  }

  function renderModalMedia() {
    modalMediaSide.innerHTML = '';
    
    const mediaList = activeItem.media || [];
    if (mediaList.length === 0) {
      modalMediaSide.innerHTML = `
        <div class="media-placeholder" style="height:100%;">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="9" cy="9" r="2"/>
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
          </svg>
          <span>[无媒体内容]</span>
        </div>
      `;
      return;
    }
    
    // Render current active media item inside the modal (True load here)
    const mediaItem = mediaList[activeMediaIndex];
    const isVideo = mediaItem.type === 'video';
    
    if (isVideo) {
      if (window.IS_SINGLE_PAGE) {
        const introLinkEl = document.querySelector('.brand-section h1 a');
        const introUrl = introLinkEl ? introLinkEl.getAttribute('href') : '#';
        const placeholder = document.createElement('div');
        placeholder.className = 'modal-video-placeholder';
        placeholder.innerHTML = `
          <a href="${introUrl}" target="_blank" class="single-page-download-link">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="32" height="32">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>查看介绍页下载</span>
          </a>
        `;
        modalMediaSide.appendChild(placeholder);
      } else {
        const videoEl = document.createElement('video');
        videoEl.className = 'modal-main-media active loaded';
        videoEl.src = mediaItem.path;
        videoEl.controls = true;
        videoEl.autoplay = true;
        videoEl.loop = true;
        modalMediaSide.appendChild(videoEl);
      }
    } else {
      const imgEl = document.createElement('img');
      imgEl.className = 'modal-main-media active loaded';
      imgEl.src = mediaItem.path;
      imgEl.alt = activeItem.title;
      modalMediaSide.appendChild(imgEl);
    }
    
    // Render slider buttons if multi-media
    if (mediaList.length > 1) {
      // Left Arrow
      const leftArrow = document.createElement('button');
      leftArrow.className = 'slide-arrow arrow-left';
      leftArrow.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      `;
      leftArrow.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateMedia(-1);
      });
      modalMediaSide.appendChild(leftArrow);
      
      // Right Arrow
      const rightArrow = document.createElement('button');
      rightArrow.className = 'slide-arrow arrow-right';
      rightArrow.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      `;
      rightArrow.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateMedia(1);
      });
      modalMediaSide.appendChild(rightArrow);
      
      // Dots Indicators
      const dotsContainer = document.createElement('div');
      dotsContainer.className = 'slideshow-dots';
      mediaList.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = `dot ${i === activeMediaIndex ? 'active' : ''}`;
        dot.addEventListener('click', (e) => {
          e.stopPropagation();
          activeMediaIndex = i;
          renderModalMedia();
        });
        dotsContainer.appendChild(dot);
      });
      modalMediaSide.appendChild(dotsContainer);
    }
  }

  function renderModalContent() {
    const item = activeItem;
    
    // Format full description with clickable URLs
    const safeDesc = item.description ? urlify(item.description) : '无正文描述';
    
    // Format timestamps/dates
    const fullDate = item.collectedAt ? item.collectedAt : (item.date ? item.date.replace(/-(\d{2})$/, ' $1:00') : '未知时间');
    
    let modalTagsHtml = '';
    if (item.tags && item.tags.length > 0) {
      modalTagsHtml = `
        <div class="modal-desc-title">收藏标签</div>
        <div class="modal-tags-flow" style="margin-bottom: 1.5rem;">
          ${item.tags.map(t => `<span class="modal-tag-item">#${t}</span>`).join('')}
        </div>
      `;
    }

    modalContentSide.innerHTML = `
      <div class="modal-category-row">
        <span class="category-badge" data-category="${item.category}">${item.category}</span>
        <span class="card-date">采集于: ${fullDate}</span>
      </div>
      <h2 class="modal-title">${item.title}</h2>
      
      <div class="modal-desc-title">收藏正文 / 描述</div>
      <div class="modal-description">${safeDesc}</div>
      
      ${modalTagsHtml}
      
      <div class="modal-desc-title">详细元数据</div>
      <div class="modal-meta-grid">
        <div class="meta-item">
          <span class="meta-label">发布作者 (Uploader)</span>
          <span class="meta-value">${item.uploader || '未知'}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">唯一编号 (ID)</span>
          <span class="meta-value">${item.id || 'N/A'}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">点赞数 / 互动</span>
          <span class="meta-value">${item.likeCount ? formatNumber(item.likeCount) + ' 赞' : '无数据'} ${item.repostCount ? ' / ' + formatNumber(item.repostCount) + ' 转发' : ''}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">相对路径</span>
          <span class="meta-value" style="font-family: var(--font-mono); font-size: 0.75rem;">./${item.folderName}</span>
        </div>
      </div>
      
      <div class="modal-footer-row">
        ${item.sourceUrl ? `
          <a href="${item.sourceUrl}" target="_blank" class="modal-source-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            访问原始链接
          </a>
        ` : '<span></span>'}
      </div>
    `;
  }

  // Search Event Handler
  let searchTimeout = null;
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    
    // Toggle clear button visibility
    if (searchQuery.trim() !== '') {
      searchClear.classList.add('visible');
    } else {
      searchClear.classList.remove('visible');
    }
    
    // Debounce search
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      renderCards();
    }, 200);
  });

  searchClear.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    searchClear.classList.remove('visible');
    renderCards();
    searchInput.focus();
  });

  // Event binding for dynamic filters is handled in renderTagFilters

  // Sort change event
  sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    renderCards();
  });

  // Layout switcher
  layoutBtnGrid.addEventListener('click', () => {
    if (currentLayout === 'grid') return;
    currentLayout = 'grid';
    layoutBtnGrid.classList.add('active');
    layoutBtnMasonry.classList.remove('active');
    
    cardsContainer.className = 'cards-container grid-view';
    renderCards();
  });

  layoutBtnMasonry.addEventListener('click', () => {
    if (currentLayout === 'masonry') return;
    currentLayout = 'masonry';
    layoutBtnMasonry.classList.add('active');
    layoutBtnGrid.classList.remove('active');
    
    cardsContainer.className = 'cards-container masonry-view';
    renderCards();
  });

  // Modal events
  modalCloseBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Timeline scrollbar logic
  const timelineIndicator = document.getElementById('timeline-indicator');
  const timelineThumb = document.getElementById('timeline-thumb');
  const timelineTooltip = document.getElementById('timeline-tooltip');
  
  let isDragging = false;
  
  function updateScrollIndicator() {
    if (isDragging) return;
    
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    
    const totalScrollable = scrollHeight - clientHeight;
    if (totalScrollable <= 0) {
      timelineIndicator.style.display = 'none';
      return;
    }
    timelineIndicator.style.display = 'flex';
    
    const percent = scrollTop / totalScrollable;
    
    // Calculate thumb position within track limits
    const trackHeight = timelineIndicator.clientHeight;
    const thumbHeight = timelineThumb.clientHeight;
    const maxTop = trackHeight - thumbHeight;
    const currentTop = percent * maxTop;
    
    timelineThumb.style.top = `${currentTop}px`;
    
    // Update tooltip text
    updateTooltipText(percent);
  }
  
  function updateTooltipText(percent) {
    // Find item currently at the top of the viewport
    const cards = Array.from(document.querySelectorAll('.card'));
    let activeItemData = null;
    
    for (const card of cards) {
      const rect = card.getBoundingClientRect();
      // First card that starts after the header area
      if (rect.bottom > 150) {
        const id = card.getAttribute('data-id');
        activeItemData = data.find(d => d.id === id);
        break;
      }
    }
    
    // If not sorted by date, or no active item data, show percentage
    const isSortedByDate = currentSort === 'date-desc' || currentSort === 'date-asc';
    
    if (isSortedByDate && activeItemData && activeItemData.date) {
      const dateParts = activeItemData.date.split('-');
      if (dateParts.length >= 2) {
        timelineTooltip.textContent = `${dateParts[0]}-${dateParts[1]}`;
      } else {
        timelineTooltip.textContent = activeItemData.date;
      }
    } else {
      timelineTooltip.textContent = `${Math.round(percent * 100)}%`;
    }
  }
  
  // Dragging event handlers
  timelineThumb.addEventListener('mousedown', (e) => {
    isDragging = true;
    timelineThumb.classList.add('dragging');
    document.body.style.cursor = 'ns-resize';
    document.body.style.userSelect = 'none';
    
    handleDrag(e);
  });
  
  function handleDrag(e) {
    if (!isDragging) return;
    
    const trackRect = timelineIndicator.getBoundingClientRect();
    const trackHeight = trackRect.height;
    const thumbHeight = timelineThumb.clientHeight;
    
    let relativeY = e.clientY - trackRect.top - (thumbHeight / 2);
    const maxTop = trackHeight - thumbHeight;
    
    if (relativeY < 0) relativeY = 0;
    if (relativeY > maxTop) relativeY = maxTop;
    
    timelineThumb.style.top = `${relativeY}px`;
    
    const percent = relativeY / maxTop;
    
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    window.scrollTo(0, percent * (scrollHeight - clientHeight));
    
    updateTooltipText(percent);
  }
  
  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      handleDrag(e);
    }
  });
  
  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      timelineThumb.classList.remove('dragging');
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }
  });
  
  // Watch window scroll and resize
  window.addEventListener('scroll', updateScrollIndicator);
  window.addEventListener('resize', updateScrollIndicator);

  // Initial Run
  updateStats();
  renderCategoryTags();
  renderCards();
});
