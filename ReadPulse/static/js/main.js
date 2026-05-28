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

function initSearchPage() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return; // not on search page

  const searchForm = document.getElementById('search-form');

  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    doSearch(searchInput.value.trim());
  });

  searchInput.focus();
}

let currentQuery = '';

async function doSearch(query) {
  if (!query) return;

  currentQuery = query;
  showLoading();

  try {
    const params = new URLSearchParams({ q: query, max_results: 24 });
    const res = await fetch(`/api/search/?${params}`);
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || 'Something went wrong.');
      return;
    }

    renderResults(data, query);
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

function renderResults(data, query) {
  const area = document.getElementById('results-area');
  const { books, total_items } = data;

  if (!books || books.length === 0) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📭</span>
        <p>No books found for "<strong>${escHtml(query)}</strong>".</p>
        <p class="status-hint">Try a different search term.</p>
      </div>`;
    return;
  }

  const infoBar = `
    <div class="results-info">
      <div class="results-count">Showing <strong>${books.length}</strong> of ${total_items.toLocaleString()} results for "<strong>${escHtml(query)}</strong>"</div>
    </div>`;

  const cards = books.map(book => buildBookCard(book)).join('');
  area.innerHTML = `${infoBar}<div class="books-grid">${cards}</div>`;

  area.querySelectorAll('.heart-btn').forEach(btn => {
    btn.addEventListener('click', () => handleHeart(btn));
  });
}

function buildBookCard(book) {
  const coverHtml = book.thumbnail
    ? `<img src="${escHtml(book.thumbnail)}" alt="${escHtml(book.title)}" loading="lazy" onerror="this.parentElement.innerHTML=noImageHtml()">`
    : noImageHtml();

  const year = book.published_date ? book.published_date.slice(0, 4) : '';
  const rating = book.average_rating
    ? `<span class="book-rating">★ ${book.average_rating}</span>` : '';

  return `
    <div class="book-card" data-id="${escHtml(book.google_books_id)}">
      <div class="book-cover">
        ${coverHtml}
        <button class="heart-btn ${book.is_favorite ? 'active' : ''}"
          aria-label="Save to favorites"
          data-book='${escAttr(JSON.stringify(book))}'
          data-active="${book.is_favorite ? '1' : '0'}">
          ${heartSvg()}
        </button>
      </div>
      <div class="book-info">
        <div class="book-title">${escHtml(book.title)}</div>
        <div class="book-author">${escHtml(book.authors || 'Unknown Author')}</div>
        <div class="book-meta">
          ${year ? `<span class="book-year">${year}</span>` : ''}
          ${rating}
        </div>
      </div>
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

// ─── Init ─────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initSearchPage();
  initFavoritesPage();
});
