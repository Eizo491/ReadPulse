/* ReadPulse – community.js */

// ─── State ────────────────────────────────────────────────────
let communityBooks = [];
let activeType = '';
let searchDebounce = null;

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initCommunityPage();
});

function initCommunityPage() {
  // Filter tabs
  document.querySelectorAll('.filter-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeType = btn.dataset.type;
      fetchCommunityBooks();
    });
  });

  // Search
  const searchInput = document.getElementById('community-search');
  const searchBtn = document.getElementById('community-search-btn');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(fetchCommunityBooks, 300);
    });
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') { clearTimeout(searchDebounce); fetchCommunityBooks(); }
    });
  }
  if (searchBtn) {
    searchBtn.addEventListener('click', () => { clearTimeout(searchDebounce); fetchCommunityBooks(); });
  }

  // Add book modal
  document.getElementById('add-book-btn').addEventListener('click', openAddModal);
  document.getElementById('add-book-close').addEventListener('click', closeAddModal);
  document.getElementById('add-manual-btn').addEventListener('click', showAddForm);
  document.getElementById('add-back-btn').addEventListener('click', showAddSearch);
  document.getElementById('add-search-btn').addEventListener('click', searchGoogleBooksForAdd);
  document.getElementById('add-search-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchGoogleBooksForAdd();
  });
  document.getElementById('add-submit-btn').addEventListener('click', submitAddBook);

  // Request modal
  document.getElementById('request-modal-close').addEventListener('click', closeRequestModal);
  document.getElementById('request-cancel-btn').addEventListener('click', closeRequestModal);
  document.getElementById('request-submit-btn').addEventListener('click', submitRequest);
  document.getElementById('request-type-select').addEventListener('change', onRequestTypeChange);

  // Swap book search
  document.getElementById('swap-search-btn').addEventListener('click', searchSwapBook);
  document.getElementById('swap-search-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchSwapBook();
  });
  document.getElementById('swap-manual-btn').addEventListener('click', showSwapForm);
  document.getElementById('swap-change-btn').addEventListener('click', showSwapMyBooks);

  // Book detail modal
  document.getElementById('book-detail-close').addEventListener('click', closeBookDetail);
  document.getElementById('book-detail-modal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeBookDetail();
  });

  // Click outside modal to close
  document.getElementById('add-book-modal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeAddModal();
  });
  document.getElementById('request-modal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeRequestModal();
  });

  // If URL hash is #add, open modal
  if (location.hash === '#add') openAddModal();

  fetchCommunityBooks();
}

// ─── Fetch & Render ───────────────────────────────────────────
async function fetchCommunityBooks() {
  const area = document.getElementById('community-area');
  const search = (document.getElementById('community-search')?.value || '').trim();

  area.innerHTML = `<div class="status-msg"><span class="status-icon">⏳</span><p>Loading community books…</p></div>`;

  let url = `/api/community/?type=${encodeURIComponent(activeType)}`;
  if (search) url += `&q=${encodeURIComponent(search)}`;

  try {
    const resp = await fetch(url);
    const data = await resp.json();
    communityBooks = data.books || [];
    renderCommunityBooks(communityBooks);
  } catch (err) {
    area.innerHTML = `<div class="status-msg"><span class="status-icon">⚠️</span><p>Failed to load books. Please try again.</p></div>`;
  }
}

function renderCommunityBooks(books) {
  const area = document.getElementById('community-area');
  if (!books.length) {
    area.innerHTML = `<div class="status-msg"><span class="status-icon">📭</span><p>No community books found.</p><p class="status-hint">Be the first to list a book!</p></div>`;
    return;
  }

  area.innerHTML = `<div class="books-grid">${books.map(bookCard).join('')}</div>`;
}

function bookCard(book) {
  const coverHtml = book.thumbnail
    ? `<img src="${escHtml(book.thumbnail)}" alt="${escHtml(book.title)}" loading="lazy" onerror="this.parentElement.innerHTML=noImageHtml()">`
    : noImageHtml();

  const typeBadge = {
    borrow: '<span class="badge badge-borrow">Borrow</span>',
    swap:   '<span class="badge badge-swap">Swap</span>',
    both:   '<span class="badge badge-borrow">Borrow</span><span class="badge badge-swap">Swap</span>',
  }[book.listing_type] || '';

  const ownerInitial = (book.owner_username || '?')[0].toUpperCase();

  const actionBtn = book.is_own
    ? `<button class="btn-ghost btn-sm" disabled style="width:100%;">Your listing</button>`
    : `<button class="btn-primary btn-sm" style="width:100%;" onclick="event.stopPropagation();openRequestModal(${book.id})">Request</button>`;

  return `
  <div class="book-card community-card" role="article" style="cursor:pointer;" onclick="openBookDetail(${book.id})" title="View details">
    <div class="book-cover">
      ${coverHtml}
      <div class="community-type-chip">${typeBadge}</div>
    </div>
    <div class="book-info">
      <div class="book-title">${escHtml(book.title)}</div>
      <div class="book-author">${escHtml(book.authors) || 'Unknown author'}</div>
      <div class="community-card-meta">
        <span class="badge badge-condition">${escHtml(book.condition)}</span>
      </div>
      <div class="book-owner-row">
        <div class="owner-avatar">${ownerInitial}</div>
        <span class="owner-name">${escHtml(book.owner_name)}</span>
      </div>
      <div class="book-card-actions">${actionBtn}</div>
    </div>
  </div>`;
}

// ─── Book Detail Modal ────────────────────────────────────────
function openBookDetail(bookId) {
  const book = communityBooks.find(b => b.id === bookId);
  if (!book) return;

  document.getElementById('detail-modal-title').textContent = book.title;

  const typeBadge = {
    borrow: '<span class="badge badge-borrow">Borrow</span>',
    swap:   '<span class="badge badge-swap">Swap</span>',
    both:   '<span class="badge badge-borrow">Borrow</span><span class="badge badge-swap">Swap</span>',
  }[book.listing_type] || '';

  const ownerInitial = (book.owner_username || '?')[0].toUpperCase();

  const descriptionHtml = book.description
    ? `<div class="cmb-section">
        <div class="cmb-section-label">About this book</div>
        <div class="cmb-description">${escHtml(book.description)}</div>
       </div>`
    : '';

  const notesHtml = book.notes
    ? `<div class="cmb-section">
        <div class="cmb-section-label">Owner's Notes</div>
        <div class="cmb-notes">${escHtml(book.notes)}</div>
       </div>`
    : '';

  const metaItems = [];
  if (book.published_date) metaItems.push(`<span><strong>Published:</strong> ${escHtml(book.published_date)}</span>`);
  if (book.publisher)      metaItems.push(`<span><strong>Publisher:</strong> ${escHtml(book.publisher)}</span>`);
  if (book.page_count)     metaItems.push(`<span><strong>Pages:</strong> ${book.page_count}</span>`);
  if (book.isbn)           metaItems.push(`<span><strong>ISBN:</strong> ${escHtml(book.isbn)}</span>`);
  if (book.categories)     metaItems.push(`<span><strong>Genre:</strong> ${escHtml(book.categories)}</span>`);

  const metaHtml = metaItems.length
    ? `<div class="cmb-section"><div class="cmb-meta-grid">${metaItems.join('')}</div></div>`
    : '';

  const contactHtml = book.contact_info
    ? `<div class="cmb-info-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 9.5a19.79 19.79 0 0 1-3-8.59A2 2 0 0 1 3.63 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 8.91a16 16 0 0 0 5.61 5.61l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        <div>
          <div class="cmb-info-label">Contact</div>
          <div class="cmb-info-value">${escHtml(book.contact_info)}</div>
        </div>
       </div>`
    : '';

  const locationHtml = book.location
    ? `<div class="cmb-info-row">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
        <div>
          <div class="cmb-info-label">Preferred Meetup Area</div>
          <div class="cmb-info-value">${escHtml(book.location)}</div>
        </div>
       </div>`
    : '';

  const contactSectionHtml = (contactHtml || locationHtml)
    ? `<div class="cmb-section">
        <div class="cmb-section-label">Contact & Meetup</div>
        <div class="cmb-contact-block">${contactHtml}${locationHtml}</div>
       </div>`
    : '';

  const actionBtn = book.is_own
    ? `<button class="btn-ghost" disabled>Your listing</button>`
    : `<button class="btn-primary" onclick="closeBookDetail();openRequestModal(${book.id})">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        Send Request
       </button>`;

  document.getElementById('book-detail-body').innerHTML = `
    <div class="cmb-book-header">
      <div class="cmb-cover">
        ${book.thumbnail
          ? `<img src="${escHtml(book.thumbnail)}" alt="${escHtml(book.title)}" style="width:100%;height:100%;object-fit:cover;border-radius:6px;">`
          : `<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:var(--bg-secondary);border-radius:6px;font-size:2.5rem;">📖</div>`}
      </div>
      <div class="cmb-header-info">
        <div class="cmb-book-title">${escHtml(book.title)}</div>
        <div class="cmb-book-author">${escHtml(book.authors) || 'Unknown author'}</div>
        <div class="detail-badges" style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;">
          ${typeBadge}
          <span class="badge badge-condition">${escHtml(book.condition)}</span>
        </div>
        <div class="book-owner-row" style="margin-top:10px;">
          <div class="owner-avatar">${ownerInitial}</div>
          <span class="owner-name">${escHtml(book.owner_name)}</span>
        </div>
      </div>
    </div>

    ${descriptionHtml}
    ${metaHtml}
    ${notesHtml}
    ${contactSectionHtml}

    <div class="modal-actions" style="margin-top:4px;">
      <button class="btn-ghost" onclick="closeBookDetail()">Close</button>
      ${actionBtn}
    </div>
  `;

  document.getElementById('book-detail-modal').hidden = false;
  document.body.style.overflow = 'hidden';
}

function closeBookDetail() {
  document.getElementById('book-detail-modal').hidden = true;
  document.body.style.overflow = '';
}

// ─── Add Book Modal ───────────────────────────────────────────
let selectedGoogleBook = null;

function openAddModal() {
  document.getElementById('add-book-modal').hidden = false;
  document.body.style.overflow = 'hidden';
  showAddSearch();
}
function closeAddModal() {
  document.getElementById('add-book-modal').hidden = true;
  document.body.style.overflow = '';
  selectedGoogleBook = null;
  document.getElementById('add-search-input').value = '';
  document.getElementById('add-search-results').innerHTML = '';
  ['form-contact-info','form-location','form-thumbnail-url'].forEach(id => {
    const el = document.getElementById(id); if (el) el.value = '';
  });
  const cp = document.getElementById('form-cover-preview'); if (cp) cp.innerHTML = '';
  const cf = document.getElementById('form-cover-file'); if (cf) cf.value = '';
}

function showAddSearch() {
  document.getElementById('add-step-search').hidden = false;
  document.getElementById('add-step-form').hidden = true;
  selectedGoogleBook = null;
}

function showAddForm(book) {
  document.getElementById('add-step-search').hidden = true;
  document.getElementById('add-step-form').hidden = false;

  // Cover group: hide if book has thumbnail from Google, show for manual
  const coverGroup = document.getElementById('form-cover-group');
  const coverPreview = document.getElementById('form-cover-preview');

  if (book && book.google_books_id) {
    selectedGoogleBook = book;
    document.getElementById('form-title').value = book.title || '';
    document.getElementById('form-authors').value = book.authors || '';
    document.getElementById('form-isbn').value = book.isbn || '';
    document.getElementById('form-published').value = book.published_date || '';
    document.getElementById('form-thumbnail').value = book.thumbnail || '';
    document.getElementById('form-description').value = book.description || '';
    document.getElementById('form-categories').value = book.categories || '';
    document.getElementById('form-page-count').value = book.page_count || '';
    document.getElementById('form-publisher').value = book.publisher || '';
    document.getElementById('form-language').value = book.language || '';
    document.getElementById('form-google-id').value = book.google_books_id || '';

    // Hide cover upload — Google Books already supplies the thumbnail
    if (coverGroup) coverGroup.hidden = true;
    if (coverPreview) coverPreview.innerHTML = '';

    document.getElementById('add-book-preview').innerHTML = `
      <div class="add-preview-inner">
        ${book.thumbnail ? `<img src="${escHtml(book.thumbnail)}" class="add-preview-thumb" alt="">` : ''}
        <div>
          <div class="add-preview-title">${escHtml(book.title)}</div>
          <div class="add-preview-author">${escHtml(book.authors)}</div>
        </div>
      </div>`;
  } else {
    // Manual entry — show cover upload
    if (coverGroup) coverGroup.hidden = false;
    document.getElementById('add-book-preview').innerHTML = '';
    document.getElementById('form-thumbnail-url').value = '';
    document.getElementById('form-cover-file').value = '';
    if (coverPreview) coverPreview.innerHTML = '';
    ['form-title','form-authors','form-isbn','form-published','form-thumbnail',
     'form-description','form-categories','form-page-count','form-publisher',
     'form-language','form-google-id'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
  }
}

async function searchGoogleBooksForAdd() {
  const q = document.getElementById('add-search-input').value.trim();
  if (!q) return;
  const resultsEl = document.getElementById('add-search-results');
  resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:8px 0;">Searching…</p>`;

  try {
    const resp = await fetch(`/api/search/?q=${encodeURIComponent(q)}&max_results=6`);
    const data = await resp.json();
    const books = data.books || [];

    if (!books.length) {
      resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:8px 0;">No results found. <button class="btn-ghost btn-sm" onclick="showAddForm()">Add manually</button></p>`;
      return;
    }

    resultsEl.innerHTML = `<div class="add-search-list">${books.map(b => `
      <div class="add-search-item" onclick='selectGoogleBook(${JSON.stringify(b).replace(/'/g, "&#39;")})'>
        ${b.thumbnail ? `<img src="${escHtml(b.thumbnail)}" class="add-search-thumb" alt="">` : `<div class="add-search-thumb-placeholder"></div>`}
        <div class="add-search-info">
          <div class="add-search-title">${escHtml(b.title)}</div>
          <div class="add-search-author">${escHtml(b.authors) || 'Unknown author'}</div>
          ${b.published_date ? `<div class="add-search-year">${escHtml(b.published_date.slice(0,4))}</div>` : ''}
        </div>
      </div>`).join('')}</div>`;
  } catch (err) {
    resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:8px 0;">Search failed. Please try again.</p>`;
  }
}

function selectGoogleBook(book) {
  showAddForm(book);
}

function onAddThumbnailUrlChange() {
  const url = document.getElementById('form-thumbnail-url').value.trim();
  document.getElementById('form-thumbnail').value = url;
  const preview = document.getElementById('form-cover-preview');
  if (url) {
    preview.innerHTML = `<div class="add-preview-inner"><img src="${escHtml(url)}" class="add-preview-thumb" alt="" onerror="this.parentElement.parentElement.innerHTML=''"><div style="font-size:.82rem;color:var(--text-muted);">Cover preview</div></div>`;
  } else {
    preview.innerHTML = '';
  }
}

function onAddCoverUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target.result;
    document.getElementById('form-thumbnail').value = dataUrl;
    document.getElementById('form-thumbnail-url').value = '';
    document.getElementById('form-cover-preview').innerHTML = `<div class="add-preview-inner"><img src="${escHtml(dataUrl)}" class="add-preview-thumb" alt=""><div style="font-size:.82rem;color:var(--text-muted);">Uploaded cover</div></div>`;
  };
  reader.readAsDataURL(file);
}

async function submitAddBook() {
  const title = document.getElementById('form-title').value.trim();
  if (!title) { showToast('Please enter a book title.', 'error'); return; }
  const contactInfo = document.getElementById('form-contact-info').value.trim();
  if (!contactInfo) { showToast('Please enter your contact info so requesters can reach you.', 'error'); return; }

  const btn = document.getElementById('add-submit-btn');
  btn.disabled = true; btn.textContent = 'Listing…';

  const payload = {
    title,
    authors: document.getElementById('form-authors').value.trim(),
    isbn: document.getElementById('form-isbn').value.trim(),
    published_date: document.getElementById('form-published').value.trim(),
    thumbnail: document.getElementById('form-thumbnail').value,
    description: document.getElementById('form-description').value,
    categories: document.getElementById('form-categories').value,
    page_count: parseInt(document.getElementById('form-page-count').value) || null,
    publisher: document.getElementById('form-publisher').value,
    language: document.getElementById('form-language').value,
    google_books_id: document.getElementById('form-google-id').value,
    listing_type: document.getElementById('form-listing-type').value,
    condition: document.getElementById('form-condition').value,
    notes: document.getElementById('form-notes').value.trim(),
    contact_info: document.getElementById('form-contact-info').value.trim(),
    location: document.getElementById('form-location').value.trim(),
  };

  try {
    const resp = await fetch('/api/community/add/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) { showToast(data.error || 'Failed to list book.', 'error'); return; }
    showToast('Book listed successfully! 🎉');
    closeAddModal();
    fetchCommunityBooks();
  } catch (err) {
    showToast('Network error. Please try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'List Book';
  }
}

// ─── Request Modal ────────────────────────────────────────────
function onRequestTypeChange() {
  const type = document.getElementById('request-type-select').value;
  const swapSection = document.getElementById('swap-offer-section');
  swapSection.hidden = (type !== 'swap');
  if (type === 'swap') {
    showSwapMyBooks();
  }
}

function openRequestModal(bookId) {
  const book = communityBooks.find(b => b.id === bookId);
  if (!book) return;

  document.getElementById('request-book-id').value = bookId;
  document.getElementById('request-modal-title').textContent = `Request: ${book.title}`;
  document.getElementById('request-book-info').innerHTML = `
    <div class="request-book-preview">
      ${book.thumbnail ? `<img src="${escHtml(book.thumbnail)}" class="req-thumb" alt="">` : ''}
      <div>
        <div class="req-book-title">${escHtml(book.title)}</div>
        <div class="req-book-author">${escHtml(book.authors)}</div>
        <div class="req-book-owner">Owner: ${escHtml(book.owner_name)}</div>
      </div>
    </div>`;

  const typeSelect = document.getElementById('request-type-select');
  typeSelect.innerHTML = '';
  if (book.listing_type === 'borrow' || book.listing_type === 'both') {
    typeSelect.add(new Option('Borrow', 'borrow'));
  }
  if (book.listing_type === 'swap' || book.listing_type === 'both') {
    typeSelect.add(new Option('Swap', 'swap'));
  }

  document.getElementById('request-message').value = '';
  document.getElementById('swap-offer-section').hidden = (typeSelect.value !== 'swap');
  if (typeSelect.value === 'swap') showSwapMyBooks();

  document.getElementById('request-modal').hidden = false;
  document.body.style.overflow = 'hidden';
  // Set min date to today
  document.getElementById('request-meetup-date').min = new Date().toISOString().split('T')[0];
  document.getElementById('request-meetup-date').value = '';
  document.getElementById('request-meetup-time').value = '';
  document.getElementById('request-meetup-location').value = '';
}

function closeRequestModal() {
  document.getElementById('request-modal').hidden = true;
  document.body.style.overflow = '';
  resetSwapForm();
}

// ─── Swap Book Source Tabs ────────────────────────────────────
function showSwapMyBooks() {
  document.getElementById('swap-mybooks-step').hidden = false;
  document.getElementById('swap-search-step').hidden = true;
  document.getElementById('swap-tab-mybooks').classList.add('active');
  document.getElementById('swap-tab-search').classList.remove('active');
  loadMyBooksForSwap();
}

function showSwapSearchTab() {
  document.getElementById('swap-mybooks-step').hidden = true;
  document.getElementById('swap-search-step').hidden = false;
  document.getElementById('swap-tab-mybooks').classList.remove('active');
  document.getElementById('swap-tab-search').classList.add('active');
}

async function loadMyBooksForSwap() {
  const resultsEl = document.getElementById('swap-mybooks-results');
  resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:6px 0;">Loading your books…</p>`;
  try {
    const resp = await fetch('/api/community/my-available-listings/');
    const data = await resp.json();
    const books = data.books || [];
    if (!books.length) {
      resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:6px 0;">You have no available listed books. <button class="btn-ghost btn-sm" onclick="showSwapSearchTab()">Search instead</button></p>`;
      return;
    }
    resultsEl.innerHTML = `<div class="swap-search-list">${books.map(b => `
      <div class="swap-search-item" onclick='selectSwapBook(${JSON.stringify({
        title: b.title,
        authors: b.authors,
        thumbnail: b.thumbnail,
        description: b.description,
        google_books_id: b.google_books_id,
        condition: b.condition,
      }).replace(/'/g, "&#39;")})'>
        ${b.thumbnail ? `<img src="${escHtml(b.thumbnail)}" class="swap-search-thumb" alt="">` : `<div class="swap-search-thumb-placeholder"></div>`}
        <div class="swap-search-info">
          <div class="swap-search-title">${escHtml(b.title)}</div>
          <div class="swap-search-author">${escHtml(b.authors) || 'Unknown author'}</div>
          <span class="badge badge-condition" style="margin-top:2px;">${escHtml(b.condition)}</span>
        </div>
      </div>`).join('')}</div>`;
  } catch {
    resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;">Failed to load. <button class="btn-ghost btn-sm" onclick="loadMyBooksForSwap()">Retry</button></p>`;
  }
}

// ─── Swap Book Search ─────────────────────────────────────────
function showSwapSearch() {
  showSwapMyBooks(); // Default to "My Listed Books" tab
}

function showSwapForm(book) {
  document.getElementById('swap-search-step').hidden = true;
  document.getElementById('swap-book-form').hidden = false;

  if (book && book.title) {
    document.getElementById('swap-title').value = book.title || '';
    document.getElementById('swap-authors').value = book.authors || '';
    document.getElementById('swap-thumbnail').value = book.thumbnail || '';
    document.getElementById('swap-description').value = book.description || '';
    document.getElementById('swap-google-id').value = book.google_books_id || '';
    document.getElementById('swap-book-preview').innerHTML = `
      <div class="swap-preview-inner">
        ${book.thumbnail ? `<img src="${escHtml(book.thumbnail)}" class="swap-preview-thumb" alt="">` : ''}
        <div>
          <div class="swap-preview-title">${escHtml(book.title)}</div>
          <div class="swap-preview-author">${escHtml(book.authors || '')}</div>
        </div>
      </div>`;
    // Pre-fill condition if available (e.g. from my listed books)
    if (book.condition) {
      const condSelect = document.getElementById('swap-condition');
      if (condSelect) condSelect.value = book.condition;
    }
  } else {
    clearSwapFields();
    document.getElementById('swap-book-preview').innerHTML = '';
  }
}

function clearSwapFields() {
  ['swap-title','swap-authors','swap-thumbnail','swap-description','swap-google-id'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const preview = document.getElementById('swap-book-preview');
  if (preview) preview.innerHTML = '';
  const results = document.getElementById('swap-search-results');
  if (results) results.innerHTML = '';
  const input = document.getElementById('swap-search-input');
  if (input) input.value = '';
}

function resetSwapForm() {
  clearSwapFields();
  document.getElementById('swap-offer-section').hidden = true;
  document.getElementById('swap-mybooks-step').hidden = false;
  document.getElementById('swap-search-step').hidden = true;
  document.getElementById('swap-book-form').hidden = true;
}

async function searchSwapBook() {
  const q = document.getElementById('swap-search-input').value.trim();
  if (!q) return;
  const resultsEl = document.getElementById('swap-search-results');
  resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:6px 0;">Searching…</p>`;

  try {
    const resp = await fetch(`/api/search/?q=${encodeURIComponent(q)}&max_results=5`);
    const data = await resp.json();
    const books = data.books || [];

    if (!books.length) {
      resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;padding:6px 0;">No results. <button class="btn-ghost btn-sm" onclick="showSwapForm()">Add manually</button></p>`;
      return;
    }

    resultsEl.innerHTML = `<div class="swap-search-list">${books.map(b => `
      <div class="swap-search-item" onclick='selectSwapBook(${JSON.stringify(b).replace(/'/g,"&#39;")})'>
        ${b.thumbnail ? `<img src="${escHtml(b.thumbnail)}" class="swap-search-thumb" alt="">` : `<div class="swap-search-thumb-placeholder"></div>`}
        <div class="swap-search-info">
          <div class="swap-search-title">${escHtml(b.title)}</div>
          <div class="swap-search-author">${escHtml(b.authors) || 'Unknown author'}</div>
        </div>
      </div>`).join('')}</div>`;
  } catch {
    resultsEl.innerHTML = `<p style="color:var(--text-muted);font-size:.85rem;">Search failed. Please try again.</p>`;
  }
}

function selectSwapBook(book) {
  showSwapForm(book);
}

async function submitRequest() {
  const bookId = parseInt(document.getElementById('request-book-id').value);
  const requestType = document.getElementById('request-type-select').value;
  const message = document.getElementById('request-message').value.trim();

  // Validate meetup
  const meetupDate = document.getElementById('request-meetup-date').value;
  const meetupTime = document.getElementById('request-meetup-time').value;
  const meetupLocation = document.getElementById('request-meetup-location').value.trim();
  if (!meetupDate || !meetupTime) { showToast('Please set a proposed meetup date and time.', 'error'); return; }
  if (!meetupLocation) { showToast('Please enter a proposed meetup location.', 'error'); return; }
  const meetupDatetime = `${meetupDate} ${meetupTime}`;

  // Validate swap offer
  if (requestType === 'swap') {
    const swapTitle = document.getElementById('swap-title').value.trim();
    if (!swapTitle) {
      showToast('Please add the book you want to offer for swap.', 'error');
      return;
    }
  }

  const btn = document.getElementById('request-submit-btn');
  btn.disabled = true; btn.textContent = 'Sending…';

  const payload = { book_id: bookId, request_type: requestType, message, meetup_datetime: meetupDatetime, meetup_location: meetupLocation };

  if (requestType === 'swap') {
    payload.swap_book_title       = document.getElementById('swap-title').value.trim();
    payload.swap_book_authors     = document.getElementById('swap-authors').value.trim();
    payload.swap_book_thumbnail   = document.getElementById('swap-thumbnail').value;
    payload.swap_book_condition   = document.getElementById('swap-condition').value;
    payload.swap_book_description = document.getElementById('swap-description').value;
    payload.swap_book_google_id   = document.getElementById('swap-google-id').value;
  }

  try {
    const resp = await fetch('/api/requests/create/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) { showToast(data.error || 'Failed to send request.', 'error'); return; }
    showToast('Request sent! 📬');
    closeRequestModal();
  } catch {
    showToast('Network error. Please try again.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Send Request';
  }
}

// ─── Helpers ──────────────────────────────────────────────────
function getCsrfToken() {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}
