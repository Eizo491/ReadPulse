/* ReadPulse – my_listings.js */

document.addEventListener('DOMContentLoaded', () => {
  loadMyListings();

  document.getElementById('listing-add-btn').addEventListener('click', e => {
    e.preventDefault();
    window.location.href = '/community/#add';
  });

  // Edit modal
  document.getElementById('edit-modal-close').addEventListener('click', () => closeModal('edit-modal'));
  document.getElementById('edit-cancel-btn').addEventListener('click', () => closeModal('edit-modal'));
  document.getElementById('edit-save-btn').addEventListener('click', saveEditListing);
  document.getElementById('edit-modal').addEventListener('click', e => { if (e.target === e.currentTarget) closeModal('edit-modal'); });

  // Delete modal
  document.getElementById('delete-modal-close').addEventListener('click', () => closeModal('delete-modal'));
  document.getElementById('delete-cancel-btn').addEventListener('click', () => closeModal('delete-modal'));
  document.getElementById('delete-confirm-btn').addEventListener('click', confirmDeleteListing);
  document.getElementById('delete-modal').addEventListener('click', e => { if (e.target === e.currentTarget) closeModal('delete-modal'); });
});

async function loadMyListings() {
  const area = document.getElementById('listings-area');
  try {
    const resp = await fetch('/api/community/my-listings/');
    const data = await resp.json();
    renderMyListings(data.books || []);
  } catch (err) {
    area.innerHTML = `<div class="status-msg"><span class="status-icon">⚠️</span><p>Failed to load listings.</p></div>`;
  }
}

function renderMyListings(books) {
  const area = document.getElementById('listings-area');

  if (!books.length) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📚</span>
        <p>You haven't listed any books yet.</p>
        <p class="status-hint">Share books with your community — they'll thank you!</p>
        <button class="btn-primary" style="margin-top:18px;" onclick="window.location.href='/community/#add'">List Your First Book</button>
      </div>`;
    return;
  }

  area.innerHTML = `<div class="listings-table-wrap"><table class="listings-table">
    <thead><tr>
      <th>Book</th>
      <th>Type</th>
      <th>Condition</th>
      <th>Status</th>
      <th>Listed</th>
      <th>Actions</th>
    </tr></thead>
    <tbody>
      ${books.map(listingRow).join('')}
    </tbody>
  </table></div>`;
}

function listingRow(book) {
  const typeLabel = {borrow:'Borrow', swap:'Swap', both:'Borrow / Swap'}[book.listing_type] || book.listing_type;
  const statusClass = {available:'status-available', borrowed:'status-borrowed', swapped:'status-swapped', unavailable:'status-unavailable'}[book.status] || '';
  const date = new Date(book.created_at).toLocaleDateString(undefined, {year:'numeric',month:'short',day:'numeric'});

  return `<tr>
    <td>
      <div class="listing-book-cell">
        ${book.thumbnail ? `<img src="${escHtml(book.thumbnail)}" class="listing-thumb" alt="" onerror="this.style.display='none'">` : '<div class="listing-thumb-placeholder"></div>'}
        <div>
          <div class="listing-title">${escHtml(book.title)}</div>
          <div class="listing-author">${escHtml(book.authors) || 'Unknown author'}</div>
        </div>
      </div>
    </td>
    <td><span class="badge badge-${book.listing_type === 'both' ? 'both' : book.listing_type}">${escHtml(typeLabel)}</span></td>
    <td>${escHtml(book.condition)}</td>
    <td><span class="status-pill ${statusClass}">${escHtml(book.status)}</span></td>
    <td style="white-space:nowrap;">${escHtml(date)}</td>
    <td>
      <div style="display:flex;gap:8px;">
        <button class="btn-ghost btn-sm" onclick="openEditModal(${JSON.stringify(book).replace(/"/g,'&quot;')})">Edit</button>
        <button class="btn-danger btn-sm" onclick="openDeleteModal(${book.id}, '${escHtml(book.title).replace(/'/g,"&#39;")}')">Remove</button>
      </div>
    </td>
  </tr>`;
}

// ─── Edit Modal ───────────────────────────────────────────────
function openEditModal(book) {
  // Basic info
  document.getElementById('edit-book-id').value = book.id;
  document.getElementById('edit-google-id').value = book.google_books_id || '';
  document.getElementById('edit-title').value = book.title || '';
  document.getElementById('edit-authors').value = book.authors || '';
  document.getElementById('edit-isbn').value = book.isbn || '';
  document.getElementById('edit-published').value = book.published_date || '';

  // Cover
  const thumb = book.thumbnail || '';
  document.getElementById('edit-thumbnail').value = thumb;
  document.getElementById('edit-thumbnail-url').value = thumb;
  renderEditCoverPreview(thumb);

  // Listing options
  document.getElementById('edit-condition').value = book.condition || 'Good';
  document.getElementById('edit-listing-type').value = book.listing_type || 'borrow';
  document.getElementById('edit-status').value = book.status || 'available';
  document.getElementById('edit-notes').value = book.notes || '';

  // Contact & meetup
  document.getElementById('edit-contact-info').value = book.contact_info || '';
  document.getElementById('edit-location').value = book.location || '';

  // Clear file input
  document.getElementById('edit-cover-file').value = '';

  document.getElementById('edit-modal').hidden = false;
  document.body.style.overflow = 'hidden';
}

function renderEditCoverPreview(url) {
  const preview = document.getElementById('edit-cover-preview');
  if (!url) { preview.innerHTML = ''; return; }
  preview.innerHTML = `
    <div class="add-preview-inner">
      <img src="${escHtml(url)}" class="add-preview-thumb" alt="" onerror="this.parentElement.parentElement.innerHTML=''">
      <div style="flex:1;">
        <div style="font-size:.82rem;color:var(--text-muted);">Current cover</div>
        <button type="button" class="btn-ghost btn-sm" style="margin-top:6px;" onclick="clearEditCover()">✕ Remove cover</button>
      </div>
    </div>`;
}

function clearEditCover() {
  document.getElementById('edit-thumbnail').value = '';
  document.getElementById('edit-thumbnail-url').value = '';
  document.getElementById('edit-cover-file').value = '';
  document.getElementById('edit-cover-preview').innerHTML = '';
}

function onEditThumbnailUrlChange() {
  const url = document.getElementById('edit-thumbnail-url').value.trim();
  document.getElementById('edit-thumbnail').value = url;
  renderEditCoverPreview(url);
}

function onEditCoverUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target.result;
    document.getElementById('edit-thumbnail').value = dataUrl;
    document.getElementById('edit-thumbnail-url').value = '';
    renderEditCoverPreview(dataUrl);
  };
  reader.readAsDataURL(file);
}

async function saveEditListing() {
  const title = document.getElementById('edit-title').value.trim();
  if (!title) { showToast('Title is required.', 'error'); return; }
  const contactInfo = document.getElementById('edit-contact-info').value.trim();
  if (!contactInfo) { showToast('Contact info is required so requesters can reach you.', 'error'); return; }

  const id = document.getElementById('edit-book-id').value;
  const payload = {
    title,
    authors:        document.getElementById('edit-authors').value.trim(),
    isbn:           document.getElementById('edit-isbn').value.trim(),
    published_date: document.getElementById('edit-published').value.trim(),
    thumbnail:      document.getElementById('edit-thumbnail').value,
    condition:      document.getElementById('edit-condition').value,
    listing_type:   document.getElementById('edit-listing-type').value,
    status:         document.getElementById('edit-status').value,
    notes:          document.getElementById('edit-notes').value.trim(),
    contact_info:   contactInfo,
    location:       document.getElementById('edit-location').value.trim(),
  };

  const btn = document.getElementById('edit-save-btn');
  btn.disabled = true; btn.textContent = 'Saving…';

  try {
    const resp = await fetch(`/api/community/${id}/`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!resp.ok) { showToast(data.error || 'Update failed.', 'error'); return; }
    showToast('Listing updated! ✅');
    closeModal('edit-modal');
    loadMyListings();
  } catch (err) {
    showToast('Network error.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Save Changes';
  }
}

// ─── Delete Modal ─────────────────────────────────────────────
function openDeleteModal(id, title) {
  document.getElementById('delete-book-id').value = id;
  document.getElementById('delete-book-title').textContent = title;
  document.getElementById('delete-modal').hidden = false;
  document.body.style.overflow = 'hidden';
}

async function confirmDeleteListing() {
  const id = document.getElementById('delete-book-id').value;
  const btn = document.getElementById('delete-confirm-btn');
  btn.disabled = true; btn.textContent = 'Removing…';

  try {
    const resp = await fetch(`/api/community/${id}/`, {
      method: 'DELETE',
      headers: {'X-CSRFToken': getCsrfToken()},
    });
    if (!resp.ok) { showToast('Failed to remove listing.', 'error'); return; }
    showToast('Listing removed.');
    closeModal('delete-modal');
    loadMyListings();
  } catch (err) {
    showToast('Network error.', 'error');
  } finally {
    btn.disabled = false; btn.textContent = 'Remove';
  }
}

// ─── Helpers ──────────────────────────────────────────────────
function closeModal(id) {
  document.getElementById(id).hidden = true;
  document.body.style.overflow = '';
}

function getCsrfToken() {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}
