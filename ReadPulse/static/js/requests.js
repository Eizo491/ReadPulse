/* ReadPulse – requests.js */

document.addEventListener('DOMContentLoaded', () => {
  initRequestsPage();
});

function initRequestsPage() {
  // Tabs
  document.querySelectorAll('.req-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.req-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tab = btn.dataset.tab;
      document.querySelectorAll('.req-panel').forEach(p => p.hidden = true);
      document.getElementById(`panel-${tab}`).hidden = false;
    });
  });

  loadMyRequests();
  loadIncomingRequests();
}

// ─── My Requests ──────────────────────────────────────────────
async function loadMyRequests() {
  const area = document.getElementById('my-requests-area');
  try {
    const resp = await fetch('/api/requests/mine/');
    const data = await resp.json();
    const requests = data.requests || [];

    const badge = document.getElementById('my-req-badge');
    if (requests.length) { badge.textContent = requests.length; badge.hidden = false; }

    renderMyRequests(requests);
  } catch (err) {
    area.innerHTML = `<div class="status-msg"><span class="status-icon">⚠️</span><p>Failed to load requests.</p></div>`;
  }
}

function renderMyRequests(requests) {
  const area = document.getElementById('my-requests-area');

  if (!requests.length) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📬</span>
        <p>You haven't made any requests yet.</p>
        <p class="status-hint">Browse the community library and request a book!</p>
        <a href="/community/" class="btn-primary" style="display:inline-flex;margin-top:16px;">Browse Books</a>
      </div>`;
    return;
  }

  area.innerHTML = `<div class="req-list">${requests.map(r => myRequestCard(r)).join('')}</div>`;
}

function myRequestCard(r) {
  const statusInfo = statusMeta(r.status);
  const date = new Date(r.created_at).toLocaleDateString(undefined, {year:'numeric',month:'short',day:'numeric'});

  let actions = '';
  if (r.status === 'pending') {
    actions = `<button class="btn-danger btn-sm" onclick="cancelRequest(${r.id})">Cancel</button>`;
  } else if (r.status === 'accepted' && r.request_type === 'borrow') {
    actions = `<button class="btn-primary btn-sm" onclick="returnBook(${r.id})">↩ Return Book</button>`;
  }

  let swapOfferHtml = '';
  if (r.request_type === 'swap' && r.swap_book_title) {
    swapOfferHtml = `
      <div class="swap-offer-block">
        <div class="swap-offer-label">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 16V4m0 0L3 8m4-4 4 4M17 8v12m0 0 4-4m-4 4-4-4"/></svg>
          Your offer:
        </div>
        <div class="swap-offer-book">
          ${r.swap_book_thumbnail ? `<img src="${escHtml(r.swap_book_thumbnail)}" class="swap-offer-thumb" alt="" onerror="this.style.display='none'">` : '<div class="swap-offer-thumb-placeholder"></div>'}
          <div class="swap-offer-info">
            <div class="swap-offer-title">${escHtml(r.swap_book_title)}</div>
            ${r.swap_book_authors ? `<div class="swap-offer-author">${escHtml(r.swap_book_authors)}</div>` : ''}
            ${r.swap_book_condition ? `<span class="badge badge-condition">${escHtml(r.swap_book_condition)}</span>` : ''}
          </div>
        </div>
      </div>`;
  }

  let meetupHtml = '';
  if (r.meetup_datetime || r.meetup_location) {
    meetupHtml = `
      <div class="meetup-block">
        <div class="meetup-label">📅 Proposed Meetup</div>
        ${r.meetup_datetime ? `<div class="meetup-row">🕐 ${escHtml(formatMeetup(r.meetup_datetime))}</div>` : ''}
        ${r.meetup_location ? `<div class="meetup-row">📍 ${escHtml(r.meetup_location)}</div>` : ''}
      </div>`;
  }

  let contactHtml = '';
  if (r.status === 'accepted' && r.book_contact_info) {
    contactHtml = `
      <div class="contact-block">
        <div class="contact-label">📞 Owner Contact</div>
        <div class="contact-value">${escHtml(r.book_contact_info)}</div>
        ${r.book_location ? `<div class="contact-area">📍 Meetup area: ${escHtml(r.book_location)}</div>` : ''}
      </div>`;
  }

  return `
  <div class="req-card">
    <div class="req-card-cover">
      ${r.book_thumbnail ? `<img src="${escHtml(r.book_thumbnail)}" alt="" onerror="this.style.display='none'">` : '<div class="req-cover-placeholder"></div>'}
    </div>
    <div class="req-card-body">
      <div class="req-card-header">
        <div>
          <div class="req-card-title">${escHtml(r.book_title)}</div>
          <div class="req-card-meta">${escHtml(r.book_authors)} · Owner: <strong>${escHtml(r.book_owner_name)}</strong></div>
        </div>
        <span class="req-status-badge ${statusInfo.cls}">${statusInfo.label}</span>
      </div>
      <div class="req-card-details">
        <span class="badge badge-${r.request_type}">${r.request_type === 'borrow' ? 'Borrow' : 'Swap'}</span>
        <span class="req-date">${date}</span>
      </div>
      ${swapOfferHtml}
      ${meetupHtml}
      ${contactHtml}
      ${r.message ? `<div class="req-message">"${escHtml(r.message)}"</div>` : ''}
      ${actions ? `<div class="req-actions">${actions}</div>` : ''}
    </div>
  </div>`;
}

async function cancelRequest(requestId) {
  if (!confirm('Cancel this request?')) return;
  try {
    const resp = await fetch(`/api/requests/${requestId}/`, {
      method: 'PATCH',
      headers: {'Content-Type':'application/json','X-CSRFToken':getCsrfToken()},
      body: JSON.stringify({status: 'cancelled'}),
    });
    if (!resp.ok) { showToast('Failed to cancel request.', 'error'); return; }
    showToast('Request cancelled.');
    loadMyRequests();
  } catch (err) {
    showToast('Network error.', 'error');
  }
}

async function returnBook(requestId) {
  if (!confirm('Mark this book as returned? The book will become available again for others.')) return;
  try {
    const resp = await fetch(`/api/requests/${requestId}/`, {
      method: 'PATCH',
      headers: {'Content-Type':'application/json','X-CSRFToken':getCsrfToken()},
      body: JSON.stringify({status: 'returned'}),
    });
    const data = await resp.json();
    if (!resp.ok) { showToast(data.error || 'Failed to return book.', 'error'); return; }
    showToast('Book returned successfully! 📚');
    loadMyRequests();
  } catch (err) {
    showToast('Network error.', 'error');
  }
}

// ─── Incoming Requests ────────────────────────────────────────
async function loadIncomingRequests() {
  const area = document.getElementById('incoming-area');
  try {
    const resp = await fetch('/api/requests/for-me/');
    const data = await resp.json();
    const requests = data.requests || [];

    const pending = requests.filter(r => r.status === 'pending').length;
    const badge = document.getElementById('incoming-badge');
    if (pending) { badge.textContent = pending; badge.hidden = false; }

    renderIncomingRequests(requests);
  } catch (err) {
    area.innerHTML = `<div class="status-msg"><span class="status-icon">⚠️</span><p>Failed to load requests.</p></div>`;
  }
}

function renderIncomingRequests(requests) {
  const area = document.getElementById('incoming-area');

  if (!requests.length) {
    area.innerHTML = `
      <div class="status-msg">
        <span class="status-icon">📭</span>
        <p>No incoming requests yet.</p>
        <p class="status-hint">When someone requests one of your books, it'll show up here.</p>
      </div>`;
    return;
  }

  area.innerHTML = `<div class="req-list">${requests.map(r => incomingRequestCard(r)).join('')}</div>`;
}

function incomingRequestCard(r) {
  const statusInfo = statusMeta(r.status);
  const date = new Date(r.created_at).toLocaleDateString(undefined, {year:'numeric',month:'short',day:'numeric'});

  let actions = '';
  if (r.status === 'pending') {
    actions = `
      <button class="btn-primary btn-sm" onclick="updateRequestStatus(${r.id}, 'accepted')">Accept</button>
      <button class="btn-danger btn-sm" onclick="updateRequestStatus(${r.id}, 'declined')">Decline</button>`;
  } else if (r.status === 'accepted') {
    actions = `<button class="btn-ghost btn-sm" onclick="updateRequestStatus(${r.id}, 'completed')">Mark Completed</button>`;
  }

  // Swap offer block shown only for swap requests with a book title
  let swapOfferHtml = '';
  if (r.request_type === 'swap' && r.swap_book_title) {
    swapOfferHtml = `
      <div class="swap-offer-block">
        <div class="swap-offer-label">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 16V4m0 0L3 8m4-4 4 4M17 8v12m0 0 4-4m-4 4-4-4"/></svg>
          Offering in exchange:
        </div>
        <div class="swap-offer-book">
          ${r.swap_book_thumbnail ? `<img src="${escHtml(r.swap_book_thumbnail)}" class="swap-offer-thumb" alt="" onerror="this.style.display='none'">` : '<div class="swap-offer-thumb-placeholder"></div>'}
          <div class="swap-offer-info">
            <div class="swap-offer-title">${escHtml(r.swap_book_title)}</div>
            ${r.swap_book_authors ? `<div class="swap-offer-author">${escHtml(r.swap_book_authors)}</div>` : ''}
            ${r.swap_book_condition ? `<span class="badge badge-condition">${escHtml(r.swap_book_condition)}</span>` : ''}
          </div>
        </div>
      </div>`;
  }

  return `
  <div class="req-card">
    <div class="req-card-cover">
      ${r.book_thumbnail ? `<img src="${escHtml(r.book_thumbnail)}" alt="" onerror="this.style.display='none'">` : '<div class="req-cover-placeholder"></div>'}
    </div>
    <div class="req-card-body">
      <div class="req-card-header">
        <div>
          <div class="req-card-title">${escHtml(r.book_title)}</div>
          <div class="req-card-meta">Requested by: <strong>${escHtml(r.requester_name)}</strong> (@${escHtml(r.requester_username)})</div>
        </div>
        <span class="req-status-badge ${statusInfo.cls}">${statusInfo.label}</span>
      </div>
      <div class="req-card-details">
        <span class="badge badge-${r.request_type}">${r.request_type === 'borrow' ? 'Borrow' : 'Swap'}</span>
        <span class="req-date">${date}</span>
      </div>
      ${swapOfferHtml}
      ${(() => { let h = ''; if (r.meetup_datetime || r.meetup_location) { h = `<div class="meetup-block"><div class="meetup-label">📅 Proposed Meetup</div>${r.meetup_datetime ? `<div class="meetup-row">🕐 ${escHtml(formatMeetup(r.meetup_datetime))}</div>` : ''}${r.meetup_location ? `<div class="meetup-row">📍 ${escHtml(r.meetup_location)}</div>` : ''}</div>`; } return h; })()}
      ${r.message ? `<div class="req-message">"${escHtml(r.message)}"</div>` : ''}
      ${actions ? `<div class="req-actions">${actions}</div>` : ''}
    </div>
  </div>`;
}

async function updateRequestStatus(requestId, status) {
  const labels = {accepted: 'Accept', declined: 'Decline', completed: 'Mark as completed'};
  if (!confirm(`${labels[status] || 'Update'} this request?`)) return;

  try {
    const resp = await fetch(`/api/requests/${requestId}/`, {
      method: 'PATCH',
      headers: {'Content-Type':'application/json','X-CSRFToken':getCsrfToken()},
      body: JSON.stringify({status}),
    });
    const data = await resp.json();
    if (!resp.ok) { showToast(data.error || 'Failed to update.', 'error'); return; }
    showToast(`Request ${status}.`);
    loadIncomingRequests();
  } catch (err) {
    showToast('Network error.', 'error');
  }
}

// ─── Helpers ──────────────────────────────────────────────────
function statusMeta(status) {
  return {
    pending:   { label: 'Pending',   cls: 'req-status-pending' },
    accepted:  { label: 'Accepted',  cls: 'req-status-accepted' },
    declined:  { label: 'Declined',  cls: 'req-status-declined' },
    completed: { label: 'Completed', cls: 'req-status-completed' },
    cancelled: { label: 'Cancelled', cls: 'req-status-cancelled' },
  }[status] || { label: status, cls: '' };
}

function getCsrfToken() {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

function formatMeetup(datetimeStr) {
  // datetimeStr is "YYYY-MM-DD HH:MM"
  try {
    const [datePart, timePart] = datetimeStr.split(' ');
    const d = new Date(`${datePart}T${timePart}`);
    const dateStr = d.toLocaleDateString(undefined, {weekday:'short', year:'numeric', month:'short', day:'numeric'});
    const timeStr = d.toLocaleTimeString(undefined, {hour:'2-digit', minute:'2-digit'});
    return `${dateStr} at ${timeStr}`;
  } catch { return datetimeStr; }
}
