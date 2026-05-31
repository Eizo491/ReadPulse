/* ReadPulse – main.js (search + favorites) */



// ─── Utilities ────────────────────────────────────────────────


function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-dot"></span>${message}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3100);
}

function escHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escAttr(str) {
  if (str == null) return '';
  return String(str).replace(/'/g, '&#39;').replace(/"/g, '&quot;');
}

function noImageHtml() {
  return `<div class="book-cover-placeholder">
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
    <span>No Cover</span>
  </div>`;
}

function heartSvg() {
  return `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
  </svg>`;
}

// ─── Search Page ──────────────────────────────────────────────

// Pagination state
let currentQuery = '';
let currentStartIndex = 0;
let currentTotalItems = 0;
const PAGE_SIZE = 24;

function initSearchPage() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return; // not on search page

  const searchForm = document.getElementById('search-form');

  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    const q = searchInput.value.trim();
    if (!q) return;
    currentStartIndex = 0;
    saveSearchState(q, 0);
    doSearch(q, 0);
  });

  searchInput.focus();

  // Restore previous search or load popular books
  const saved = getSavedSearchState();
  if (saved && saved.query) {
    searchInput.value = saved.query;
    doSearch(saved.query, saved.startIndex || 0);
  } else {
    loadFeaturedBooks();
  }
}

function saveSearchState(query, startIndex) {
  sessionStorage.setItem('rp_search', JSON.stringify({ query, startIndex }));
}

function getSavedSearchState() {
  try { return JSON.parse(sessionStorage.getItem('rp_search')); }
  catch { return null; }
}

function clearSearchState() {
  sessionStorage.removeItem('rp_search');
}

async function loadFeaturedBooks() {
  const area = document.getElementById('results-area');

  // Show a soft loading state
  area.innerHTML = `
    <div class="featured-header">
      <span class="featured-label">🔥 Popular Books</span>
      <span class="featured-hint">Search above to find any book</span>
    </div>
    <div class="skeleton-grid">${Array.from({ length: 12 }, () => `
      <div class="skeleton-card">
        <div class="skeleton-cover"></div>
        <div class="skeleton-info">
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>`).join('')}</div>`;

  // Rotate through a few curated high-rating queries so results feel fresh
  const featuredQueries = [
    'bestseller fiction',
    'popular novels',
    'most read books',
    'trending books',
  ];
  const q = featuredQueries[Math.floor(Math.random() * featuredQueries.length)];

  try {
    const params = new URLSearchParams({ q, max_results: 24 });
    const res = await fetch(`/api/search/?${params}`);
    const data = await res.json();

    if (!res.ok || !data.books || data.books.length === 0) {
      // Fallback: show a friendly message if featured load fails
      area.innerHTML = `
        <div class="status-msg">
          <span class="status-icon">📚</span>
          <p>Search for a book to get started.</p>
          <p class="status-hint">Try "Harry Potter", "Atomic Habits", or any author name.</p>
        </div>`;
      return;
    }

    // Sort by rating descending
    const sorted = [...data.books].sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0));

    const cards = sorted.map(book => buildBookCard(book)).join('');
    area.innerHTML = `
      <div class="featured-header">
        <span class="featured-label">🔥 Popular Books</span>
        <span class="featured-hint">Search above to find any book</span>
      </div>
      <div class="books-grid">${cards}</div>`;

    area.querySelectorAll('.heart-btn').forEach(btn => {
      btn.addEventListener('click', () => handleHeart(btn));
    });
  } catch (err) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📚</span>
        <p>Search for a book to get started.</p>
        <p class="status-hint">Try "Harry Potter", "Atomic Habits", or any author name.</p>
      </div>`;
  }
}

async function doSearch(query, startIndex = 0) {
  currentQuery = query;
  currentStartIndex = startIndex;
  showLoading();

  try {
    // Fetch books (Open Library) and audiobooks (LibriVox) in parallel
    const booksPage = Math.floor(startIndex / PAGE_SIZE) + 1;
    const [booksRes, abRes] = await Promise.all([
      fetch(`/api/search/?${new URLSearchParams({ q: query, max_results: PAGE_SIZE, start_index: startIndex })}`),
      fetch(`/api/search-audiobooks/?${new URLSearchParams({ q: query, page: booksPage })}`),
    ]);

    const booksData = await booksRes.json();
    const abData = await abRes.json();

    if (!booksRes.ok) {
      showError(booksData.error || 'Something went wrong.');
      return;
    }

    currentTotalItems = booksData.total_items || 0;
    renderResults(booksData, abData, query, startIndex);
  } catch (err) {
    showError('Network error. Please try again.');
  }
}

function showLoading() {
  const area = document.getElementById('results-area');
  const skeletons = Array.from({ length: 12 }, () => `
    <div class="skeleton-card">
      <div class="skeleton-cover"></div>
      <div class="skeleton-info">
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
      </div>
    </div>
  `).join('');
  area.innerHTML = `<div class="skeleton-grid">${skeletons}</div>`;
}

function showError(msg) {
  document.getElementById('results-area').innerHTML = `
    <div class="status-msg">
      <span class="status-icon">⚠️</span>
      <p>${msg}</p>
    </div>`;
}

function renderResults(booksData, abData, query, startIndex) {
  const area = document.getElementById('results-area');
  const { books, total_items } = booksData;
  const audiobooks = abData ? (abData.audiobooks || []) : [];

  if ((!books || books.length === 0) && audiobooks.length === 0) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📭</span>
        <p>No results found for "<strong>${escHtml(query)}</strong>".</p>
        <p class="status-hint">Try a different search term.</p>
      </div>`;
    return;
  }

  const pageNum = Math.floor(startIndex / PAGE_SIZE) + 1;
  const totalPages = Math.ceil(Math.min(total_items, 1000) / PAGE_SIZE);
  const hasPrev = startIndex > 0;
  const hasNext = books && books.length > 0 && startIndex + books.length < Math.min(total_items, 1000);

  // ── Books section ──
  let booksSection = '';
  if (books && books.length > 0) {
    const infoBar = `
      <div class="results-info">
        <div class="results-count">
          <strong>📖 Books</strong> — Showing <strong>${startIndex + 1}–${startIndex + books.length}</strong> of ${total_items.toLocaleString()} results for "<strong>${escHtml(query)}</strong>"
        </div>
        <div class="pagination-info">Page ${pageNum} of ${totalPages.toLocaleString()}</div>
      </div>`;

    const cards = books.map(book => buildBookCard(book)).join('');

    const pagination = `
      <div class="pagination-bar">
        <button class="btn-page btn-prev" ${hasPrev ? '' : 'disabled'} onclick="goToPage(${startIndex - PAGE_SIZE})">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 18l-6-6 6-6"/></svg>
          Previous
        </button>
        <span class="page-indicator">Page ${pageNum}</span>
        <button class="btn-page btn-next" ${hasNext ? '' : 'disabled'} onclick="goToPage(${startIndex + PAGE_SIZE})">
          Next
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>`;

    booksSection = `${infoBar}<div class="books-grid">${cards}</div>${pagination}`;
  } else {
    booksSection = `
      <div class="results-section-header">📖 Books</div>
      <div class="status-msg status-msg-inline">
        <span class="status-icon">📭</span>
        <p>No books found for "<strong>${escHtml(query)}</strong>".</p>
      </div>`;
  }

  // ── Audiobooks section ──
  let abSection = '';
  if (audiobooks.length > 0) {
    const abCards = audiobooks.map(ab => buildAudiobookCard(ab)).join('');
    abSection = `
      <div class="results-section-divider"></div>
      <div class="results-info">
        <div class="results-count"><strong>🎧 Audiobooks</strong> — Free public domain audiobooks from LibriVox</div>
      </div>
      <div class="books-grid">${abCards}</div>`;
  } else {
    abSection = `
      <div class="results-section-divider"></div>
      <div class="results-info">
        <div class="results-count"><strong>🎧 Audiobooks</strong></div>
      </div>
      <div class="status-msg status-msg-inline">
        <span class="status-icon">🎙️</span>
        <p>No audiobooks found for "<strong>${escHtml(query)}</strong>".</p>
        <p class="status-hint">LibriVox offers free public domain recordings.</p>
      </div>`;
  }

  area.innerHTML = booksSection + abSection;

  area.querySelectorAll('.heart-btn').forEach(btn => {
    btn.addEventListener('click', () => handleHeart(btn));
  });

  // Scroll to top of results
  area.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buildAudiobookCard(ab) {
  const detailUrl = ab.url_librivox || '#';
  const title = escHtml(ab.title || 'Unknown Title');
  const author = escHtml(ab.authors || 'Unknown Author');
  const lang = ab.language ? `<span class="book-year">${escHtml(ab.language)}</span>` : '';
  const duration = ab.totaltime ? `<span class="book-rating">⏱ ${escHtml(ab.totaltime)}</span>` : '';
  const year = ab.published ? `<span class="book-year">${escHtml(String(ab.published))}</span>` : '';

  return `
    <div class="book-card audiobook-card" role="article">
      <a href="${detailUrl}" target="_blank" rel="noopener" class="book-card-link" aria-label="Listen to ${title} on LibriVox">
        <div class="book-cover audiobook-cover-placeholder">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          <span>Audiobook</span>
        </div>
        <div class="book-info">
          <div class="book-title">${title}</div>
          <div class="book-author">${author}</div>
          <div class="book-meta">
            ${year}${lang}${duration}
          </div>
        </div>
      </a>
      ${ab.url_librivox ? `
      <a href="${escHtml(ab.url_librivox)}" target="_blank" rel="noopener"
         class="audiobook-listen-btn" aria-label="Listen on LibriVox" title="Listen on LibriVox">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
        Listen
      </a>` : ''}
    </div>`;
}

function goToPage(startIndex) {
  if (!currentQuery) return;
  const idx = Math.max(0, startIndex);
  saveSearchState(currentQuery, idx);
  doSearch(currentQuery, idx);
}

function buildBookCard(book) {
  const coverHtml = book.thumbnail
    ? `<img src="${escHtml(book.thumbnail)}" alt="${escHtml(book.title)}" loading="lazy" onerror="this.parentElement.innerHTML=noImageHtml()">`
    : noImageHtml();

  const year = book.published_date ? book.published_date.slice(0, 4) : '';
  const rating = book.average_rating
    ? `<span class="book-rating">★ ${book.average_rating}</span>` : '';

  const detailUrl = `/books/${encodeURIComponent(book.google_books_id)}/`;
  return `
    <div class="book-card" data-id="${escHtml(book.google_books_id)}" role="article">
      <a href="${detailUrl}" class="book-card-link" aria-label="View details for ${escHtml(book.title)}">
        <div class="book-cover">${coverHtml}</div>
        <div class="book-info">
          <div class="book-title">${escHtml(book.title)}</div>
          <div class="book-author">${escHtml(book.authors || 'Unknown Author')}</div>
          <div class="book-meta">
            ${year ? `<span class="book-year">${year}</span>` : ''}
            ${rating}
          </div>
        </div>
      </a>
      <button class="heart-btn ${book.is_favorite ? 'active' : ''}"
        aria-label="Save to favorites"
        data-book='${escAttr(JSON.stringify(book))}'
        data-active="${book.is_favorite ? '1' : '0'}">
        ${heartSvg()}
      </button>
    </div>`;
}

// ─── Heart / Favorite (search page) ──────────────────────────

async function handleHeart(btn) {
  const isActive = btn.dataset.active === '1';
  const book = JSON.parse(btn.dataset.book);

  btn.classList.add('pulse');
  btn.addEventListener('animationend', () => btn.classList.remove('pulse'), { once: true });

  if (isActive) {
    try {
      const res = await fetch(`/api/favorites/${encodeURIComponent(book.google_books_id)}/remove/`, {
        method: 'DELETE',
      });
      if (res.ok) {
        btn.dataset.active = '0';
        btn.classList.remove('active');
        showToast('Removed from favorites.', 'success');
        updateFavBadge(-1);
      } else {
        showToast('Failed to remove.', 'error');
      }
    } catch {
      showToast('Network error.', 'error');
    }
  } else {
    try {
      const res = await fetch('/api/favorites/add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(book),
      });
      if (res.ok) {
        btn.dataset.active = '1';
        btn.classList.add('active');
        showToast('Saved to favorites! ❤️', 'success');
        updateFavBadge(1);
      } else {
        showToast('Failed to save.', 'error');
      }
    } catch {
      showToast('Network error.', 'error');
    }
  }
}

function updateFavBadge(delta) {
  const badge = document.querySelector('.fav-badge');
  if (!badge) return;
  const current = parseInt(badge.textContent, 10) || 0;
  const next = Math.max(0, current + delta);
  badge.textContent = next;
  badge.style.display = next === 0 ? 'none' : '';
}

// ─── Favorites Page ───────────────────────────────────────────

function initFavoritesPage() {
  const favArea = document.getElementById('fav-area');
  if (!favArea) return; // not on favorites page

  document.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', () => removeFromFavorites(btn));
  });
}

async function removeFromFavorites(btn) {
  const googleId = btn.dataset.id;
  const card = document.querySelector(`.fav-card[data-id="${CSS.escape(googleId)}"]`);

  try {
    const res = await fetch(`/api/favorites/${encodeURIComponent(googleId)}/remove/`, {
      method: 'DELETE',
    });
    if (res.ok) {
      card.style.transition = 'opacity 0.3s, transform 0.3s';
      card.style.opacity = '0';
      card.style.transform = 'scale(0.95)';
      setTimeout(() => {
        card.remove();
        updateFavCount(-1);
        checkFavEmpty();
      }, 300);
      showToast('Removed from favorites.', 'success');
    } else {
      showToast('Failed to remove.', 'error');
    }
  } catch {
    showToast('Network error.', 'error');
  }
}

function updateFavCount(delta) {
  const countEl = document.getElementById('fav-count');
  if (countEl) {
    countEl.textContent = Math.max(0, (parseInt(countEl.textContent, 10) || 0) + delta);
  }
  updateFavBadge(delta);
}

function checkFavEmpty() {
  const grid = document.getElementById('fav-grid');
  if (grid && grid.children.length === 0) {
    document.getElementById('fav-area').innerHTML = `
      <div class="status-msg">
        <span class="status-icon">🤍</span>
        <p>Your favorites list is empty.</p>
        <p class="status-hint"><a href="/" style="color:var(--accent)">Search for books</a> and tap the heart to save them here.</p>
      </div>`;
  }
}

// ─── Book Detail Page ─────────────────────────────────────────

function initDetailPage() {
  if (typeof BOOK_ID === 'undefined') return; // not on detail page
  loadBookDetail(BOOK_ID);
}

async function loadBookDetail(id) {
  try {
    const res = await fetch(`/api/books/${encodeURIComponent(id)}/`);
    const data = await res.json();
    if (!res.ok) {
      renderDetailError(data.error || 'Could not load book details.');
      return;
    }
    renderBookDetail(data.book);
  } catch (err) {
    renderDetailError('Network error. Please try again.');
  }
}

function renderDetailError(msg) {
  document.getElementById('detail-area').innerHTML = `
    <div class="status-msg">
      <span class="status-icon">⚠️</span>
      <p>${msg}</p>
      <a href="javascript:history.back()" style="color:var(--accent);font-size:0.9rem;">← Go back</a>
    </div>`;
}

function renderBookDetail(book) {
  document.getElementById('detail-heading').textContent = book.title;
  document.title = `${book.title} – ReadPulse`;

  const coverHtml = book.thumbnail
    ? `<img src="${escHtml(book.thumbnail)}" alt="${escHtml(book.title)}" class="detail-cover-img">`
    : `<div class="detail-cover-placeholder">${noImageHtml()}</div>`;

  const stars = book.average_rating
    ? `${'★'.repeat(Math.round(book.average_rating))}${'☆'.repeat(5 - Math.round(book.average_rating))}`
    : '';

  const ratingHtml = book.average_rating ? `
    <div class="detail-rating">
      <span class="detail-stars">${stars}</span>
      <span class="detail-rating-num">${book.average_rating} / 5</span>
      ${book.ratings_count ? `<span class="detail-rating-count">(${book.ratings_count.toLocaleString()} ratings)</span>` : ''}
    </div>` : '';

  const metaItems = [
    book.authors     && { label: 'Author',     value: book.authors },
    book.publisher   && { label: 'Publisher',  value: book.publisher },
    book.published_date && { label: 'Published', value: book.published_date },
    book.page_count  && { label: 'Pages',      value: book.page_count.toLocaleString() },
    book.language    && { label: 'Language',   value: book.language.toUpperCase() },
    book.categories  && { label: 'Categories', value: book.categories },
    book.isbn        && { label: 'ISBN',       value: book.isbn },
  ].filter(Boolean);

  const metaHtml = metaItems.map(m => `
    <div class="detail-meta-row">
      <span class="detail-meta-label">${m.label}</span>
      <span class="detail-meta-value">${escHtml(String(m.value))}</span>
    </div>`).join('');

  const linksHtml = [
    book.preview_link && `<a href="${escHtml(book.preview_link)}" target="_blank" rel="noopener" class="btn-detail-link btn-preview">Preview on Google Books</a>`,
    book.buy_link     && `<a href="${escHtml(book.buy_link)}" target="_blank" rel="noopener" class="btn-detail-link btn-buy">Buy this Book</a>`,
  ].filter(Boolean).join('');

  const descHtml = book.description
    ? `<div class="detail-description">${book.description}</div>`
    : `<p class="detail-no-desc">No description available for this book.</p>`;

  document.getElementById('detail-area').innerHTML = `
    <div class="detail-layout">

      <!-- Left: Cover + Actions -->
      <div class="detail-left">
        <div class="detail-cover">${coverHtml}</div>

        <button class="heart-btn detail-heart ${book.is_favorite ? 'active' : ''}"
          aria-label="Save to favorites"
          data-book='${escAttr(JSON.stringify(book))}'
          data-active="${book.is_favorite ? '1' : '0'}">
          ${heartSvg()}
          <span class="detail-heart-label">${book.is_favorite ? 'Saved to Favorites' : 'Save to Favorites'}</span>
        </button>

        <button class="btn-read-book" id="btn-read-book" data-id="${escHtml(book.google_books_id)}" data-title="${escAttr(book.title)}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          Read Book
        </button>

        ${linksHtml ? `<div class="detail-links">${linksHtml}</div>` : ''}
      </div>

      <!-- Right: Info -->
      <div class="detail-right">
        <h1 class="detail-title">${escHtml(book.title)}</h1>
        ${book.subtitle ? `<p class="detail-subtitle">${escHtml(book.subtitle)}</p>` : ''}
        ${ratingHtml}

        <div class="detail-meta-table">${metaHtml}</div>

        <div class="detail-section-title">About this Book</div>
        ${descHtml}
      </div>

    </div>`;

  // Wire up the heart button on the detail page
  const heartBtn = document.querySelector('.detail-heart');
  if (heartBtn) {
    heartBtn.addEventListener('click', () => handleDetailHeart(heartBtn));
  }

  // Wire up the Read Book button
  const readBtn = document.getElementById('btn-read-book');
  if (readBtn) {
    readBtn.addEventListener('click', () => openReader(book));
  }
}

async function handleDetailHeart(btn) {
  const isActive = btn.dataset.active === '1';
  const book = JSON.parse(btn.dataset.book);
  const label = btn.querySelector('.detail-heart-label');

  btn.classList.add('pulse');
  btn.addEventListener('animationend', () => btn.classList.remove('pulse'), { once: true });

  if (isActive) {
    try {
      const res = await fetch(`/api/favorites/${encodeURIComponent(book.google_books_id)}/remove/`, { method: 'DELETE' });
      if (res.ok) {
        btn.dataset.active = '0';
        btn.classList.remove('active');
        if (label) label.textContent = 'Save to Favorites';
        showToast('Removed from favorites.', 'success');
        updateFavBadge(-1);
      } else { showToast('Failed to remove.', 'error'); }
    } catch { showToast('Network error.', 'error'); }
  } else {
    try {
      const res = await fetch('/api/favorites/add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(book),
      });
      if (res.ok) {
        btn.dataset.active = '1';
        btn.classList.add('active');
        if (label) label.textContent = 'Saved to Favorites';
        showToast('Saved to favorites! ❤️', 'success');
        updateFavBadge(1);
      } else { showToast('Failed to save.', 'error'); }
    } catch { showToast('Network error.', 'error'); }
  }
}

// ─── Init ─────────────────────────────────────────────────────


// Reader Modal
let googleBooksApiLoaded = false;

function initReaderModal() {
  const modal = document.getElementById('reader-modal');
  const closeBtn = document.getElementById('reader-close-btn');
  if (!modal) return;

  closeBtn.addEventListener('click', closeReader);
  modal.addEventListener('click', e => { if (e.target === modal) closeReader(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) closeReader(); });

  if (typeof google !== 'undefined' && google.books && google.books.DefaultViewer) {
    googleBooksApiLoaded = true;
  } else if (typeof google !== 'undefined' && google.books) {
    google.books.load();
    google.books.setOnLoadCallback(() => { googleBooksApiLoaded = true; });
  }
}

function openReader(book) {
  const modal = document.getElementById('reader-modal');
  const titleEl = document.getElementById('reader-modal-title');
  const viewerEl = document.getElementById('reader-viewer');
  const unavailableEl = document.getElementById('reader-unavailable');
  const fallbackLinks = document.getElementById('reader-fallback-links');

  viewerEl.innerHTML = '';
  viewerEl.style.display = 'block';
  unavailableEl.hidden = true;
  titleEl.textContent = book.title;
  modal.hidden = false;
  document.body.style.overflow = 'hidden';

  viewerEl.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;height:100%;flex-direction:column;gap:12px;color:var(--text-muted);">
      <div class="reader-spinner"></div>
      <span style="font-size:0.9rem;">Loading preview\u2026</span>
    </div>`;

  function tryEmbed() {
    viewerEl.innerHTML = '';
    const viewer = new google.books.DefaultViewer(viewerEl);
    viewer.load(
      book.google_books_id,
      () => {
        viewerEl.style.display = 'none';
        unavailableEl.hidden = false;
        fallbackLinks.innerHTML = [
          book.preview_link ? `<a href="${escHtml(book.preview_link)}" target="_blank" rel="noopener" class="btn-detail-link btn-preview">Open on Google Books</a>` : '',
          book.buy_link     ? `<a href="${escHtml(book.buy_link)}" target="_blank" rel="noopener" class="btn-detail-link btn-buy">Buy this Book</a>` : '',
        ].join('');
      },
      () => {}
    );
  }

  if (googleBooksApiLoaded) {
    tryEmbed();
  } else {
    let tries = 0;
    const poll = setInterval(() => {
      tries++;
      if (typeof google !== 'undefined' && google.books && google.books.DefaultViewer) {
        clearInterval(poll);
        googleBooksApiLoaded = true;
        tryEmbed();
      } else if (tries > 30) {
        clearInterval(poll);
        viewerEl.style.display = 'none';
        unavailableEl.hidden = false;
        fallbackLinks.innerHTML = book.preview_link
          ? `<a href="${escHtml(book.preview_link)}" target="_blank" rel="noopener" class="btn-detail-link btn-preview">Open on Google Books</a>`
          : '';
      }
    }, 100);
  }
}

function closeReader() {
  const modal = document.getElementById('reader-modal');
  if (!modal) return;
  modal.hidden = true;
  document.body.style.overflow = '';
  const viewerEl = document.getElementById('reader-viewer');
  if (viewerEl) viewerEl.innerHTML = '';
}

document.addEventListener('DOMContentLoaded', () => {
  initSearchPage();
  initFavoritesPage();
  initDetailPage();
  initReaderModal();
});

// Re-load state when user navigates back (bfcache restore)
window.addEventListener('pageshow', e => {
  if (e.persisted) {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    const saved = getSavedSearchState();
    if (saved && saved.query) {
      searchInput.value = saved.query;
      doSearch(saved.query, saved.startIndex || 0);
    } else if (!currentQuery) {
      loadFeaturedBooks();
    }
  }
});
