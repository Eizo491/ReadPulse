/* community.js – ReadPulse Community Books */
(function () {
  'use strict';


  // Safely parse a fetch Response as JSON — never throws a DOCTYPE error.
  // If the server returns HTML (e.g. Django 403/404/500 page), we get a
  // clean error message instead of "unexpected token <DOCTYPE".
  async function safeJson(res) {
    const text = await res.text();
    try {
      return JSON.parse(text);
    } catch (_) {
      throw new Error(`Server error (${res.status}). Please try again.`);
    }
  }

  // ── Session API helpers (replaces localStorage) ──────────────────────
  async function sessionGetMyBooks() {
    try {
      const res = await fetch('/api/session/my-books/');
      const d = await safeJson(res);
      return d.ids || [];
    } catch (_) { return []; }
  }
  async function sessionAddMyBook(id) {
    try {
      const res = await fetch('/api/session/my-books/add/', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id})
      });
      const d = await safeJson(res);
      return d.ids || [];
    } catch (_) { return []; }
  }
  async function sessionRemoveMyBook(id) {
    try {
      const res = await fetch(`/api/session/my-books/${id}/remove/`, {method: 'DELETE'});
      const d = await safeJson(res);
      return d.ids || [];
    } catch (_) { return []; }
  }
  // ── My Requests: server-session helpers (mirrors My Books pattern) ──
  async function sessionAddMyRequest(id) {
    try {
      const res = await fetch('/api/session/my-requests/add/', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id})
      });
      const d = await safeJson(res);
      return d.ids || [];
    } catch (_) { return []; }
  }
  async function sessionRemoveMyRequest(id) {
    try {
      const res = await fetch(`/api/session/my-requests/${id}/remove/`, {method: 'DELETE'});
      const d = await safeJson(res);
      return d.ids || [];
    } catch (_) { return []; }
  }
  // ─────────────────────────────────────────────────────────────────────

  function toast(msg, type = 'success') {
    const c = document.getElementById('toast-container');
    if (!c) return;
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.classList.add('toast-visible'), 10);
    setTimeout(() => { t.classList.remove('toast-visible'); setTimeout(() => t.remove(), 300); }, 3200);
  }

  function conditionLabel(v) {
    return { new: 'New', like_new: 'Like New', good: 'Good', fair: 'Fair', worn: 'Worn' }[v] || v;
  }

  function statusClass(s) {
    return { pending: 'status-pending', approved: 'status-approved', declined: 'status-declined', returned: 'status-returned' }[s] || '';
  }

  function coverHTML(book, cls = '') {
    if (book.thumbnail) {
      return `<img src="${book.thumbnail}" alt="${book.title}" class="${cls}" onerror="this.parentElement.innerHTML='<div class=\\'book-cover-placeholder\\'><svg width=\\'32\\' height=\\'32\\' viewBox=\\'0 0 24 24\\' fill=\\'none\\' stroke=\\'currentColor\\' stroke-width=\\'1.5\\'><path d=\\'M4 19.5A2.5 2.5 0 0 1 6.5 17H20\\'/><path d=\\'M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z\\'/></svg></div>'">`; 
    }
    return `<div class="book-cover-placeholder"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></div>`;
  }

  // ══════════════════════════════════════════════════════════════════════
  // COMMUNITY LISTING PAGE
  // ══════════════════════════════════════════════════════════════════════
  const grid = document.getElementById('community-grid');
  if (grid) {
    const loading = document.getElementById('community-loading');
    const empty   = document.getElementById('community-empty');
    const stats   = document.getElementById('community-stats');
    let allBooks  = [];
    let debounce;

    // ── Render ──
    function renderGrid(books) {
      grid.innerHTML = '';
      if (!books.length) {
        grid.style.display = 'none';
        empty.style.display = '';
        if (stats) stats.textContent = 'No books found.';
        return;
      }
      grid.style.display = '';
      empty.style.display = 'none';
      if (stats) {
        const avail = books.filter(b => b.is_available).length;
        stats.textContent = `${books.length} book${books.length !== 1 ? 's' : ''} listed · ${avail} available to borrow`;
      }
      books.forEach(book => {
        const card = document.createElement('a');
        card.className = 'community-card';
        card.href = `/community/${book.id}/`;
        const chip = book.is_available
          ? '<span class="availability-chip available">Available</span>'
          : '<span class="availability-chip unavailable">Borrowed</span>';
        const listingChip = book.listing_type === 'swap'
          ? '<span class="listing-type-chip listing-type-swap">Swap</span>'
          : book.listing_type === 'both'
          ? '<span class="listing-type-chip listing-type-both">Borrow/Swap</span>'
          : '<span class="listing-type-chip listing-type-borrow">Borrow</span>';
        card.innerHTML = `
          <div class="community-card-cover">
            ${coverHTML(book)}
            ${chip}
            ${listingChip}
          </div>
          <div class="community-card-body">
            <div class="community-card-title">${book.title}</div>
            ${book.authors ? `<div class="community-card-author">${book.authors}</div>` : ''}
            <div class="community-card-footer">
              <div class="community-card-owner">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
                ${book.owner_name}
              </div>
              ${book.location ? `<div class="community-card-location">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                ${book.location}
              </div>` : ''}
            </div>
          </div>`;
        grid.appendChild(card);
      });
    }

    // ── Load ──
    async function loadBooks(q = '') {
      loading.style.display = '';
      grid.style.display = 'none';
      empty.style.display = 'none';
      try {
        const url = '/api/community/' + (q ? `?q=${encodeURIComponent(q)}` : '');
        const res = await fetch(url);
        const data = await safeJson(res);
        allBooks = data.books || [];
        renderGrid(allBooks);
      } catch (e) {
        toast('Failed to load books. Please refresh.', 'error');
      } finally {
        loading.style.display = 'none';
      }
    }

    loadBooks();

    // ── Search ──
    const searchInput = document.getElementById('community-search');
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => loadBooks(searchInput.value.trim()), 350);
      });
    }

    // ── Add Book Modal ──
    const addModal    = document.getElementById('add-modal');
    const openBtn     = document.getElementById('open-add-modal');
    const closeBtn    = document.getElementById('close-add-modal');
    const emptyAddBtn = document.getElementById('empty-add-btn');
    const stepPick    = document.getElementById('step-pick');
    const stepForm    = document.getElementById('step-form');
    const manualBtn   = document.getElementById('btn-manual');
    const backBtn     = document.getElementById('btn-back-to-pick');

    function openModal() { addModal.style.display = 'flex'; resetModal(); }
    function closeModal() { addModal.style.display = 'none'; coverDataUrl = null; }
    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (emptyAddBtn) emptyAddBtn.addEventListener('click', openModal);
    if (addModal) addModal.addEventListener('click', e => { if (e.target === addModal) closeModal(); });

    function resetModal() {
      stepPick.style.display = '';
      stepForm.style.display = 'none';
      document.getElementById('modal-book-search').value = '';
      document.getElementById('modal-search-results').innerHTML = '';
      clearForm();
    }

    // ── Cover image handling ──
    let coverDataUrl = null;

    function clearForm() {
      ['f-title','f-authors','f-owner-name','f-owner-contact','f-location','f-notes',
       'f-thumbnail','f-google-books-id','f-published-date','f-categories'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      document.getElementById('f-condition').value = 'good';
      const sel = document.getElementById('form-selected-book');
      if (sel) sel.style.display = 'none';
      coverDataUrl = null;
      resetCoverPreview();
    }

    function resetCoverPreview() {
      const preview = document.getElementById('cover-preview');
      const placeholder = document.getElementById('cover-placeholder');
      const img = document.getElementById('cover-preview-img');
      if (preview) preview.style.display = 'none';
      if (placeholder) placeholder.style.display = '';
      if (img) img.src = '';
      const fileInput = document.getElementById('f-cover-upload');
      if (fileInput) fileInput.value = '';
    }

    function setCoverPreview(src) {
      const preview = document.getElementById('cover-preview');
      const placeholder = document.getElementById('cover-placeholder');
      const img = document.getElementById('cover-preview-img');
      if (img) img.src = src;
      if (preview) preview.style.display = '';
      if (placeholder) placeholder.style.display = 'none';
    }

    // Cover upload input
    const coverUploadInput = document.getElementById('f-cover-upload');
    if (coverUploadInput) {
      coverUploadInput.addEventListener('change', () => {
        const file = coverUploadInput.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
          toast('Please select an image file.', 'error');
          return;
        }
        if (file.size > 5 * 1024 * 1024) {
          toast('Image must be under 5MB.', 'error');
          return;
        }
        const reader = new FileReader();
        reader.onload = e => {
          coverDataUrl = e.target.result;
          const thumbInput = document.getElementById('f-thumbnail');
          if (thumbInput) thumbInput.value = '';
          setCoverPreview(coverDataUrl);
        };
        reader.readAsDataURL(file);
      });
    }

    // Remove cover button
    const removeCoverBtn = document.getElementById('btn-remove-cover');
    if (removeCoverBtn) {
      removeCoverBtn.addEventListener('click', () => {
        coverDataUrl = null;
        resetCoverPreview();
      });
    }

    // Show form from manual
    if (manualBtn) manualBtn.addEventListener('click', () => {
      stepPick.style.display = 'none';
      stepForm.style.display = '';
    });
    if (backBtn) backBtn.addEventListener('click', () => {
      stepPick.style.display = '';
      stepForm.style.display = 'none';
    });

    // Google Books search in modal
    const modalSearchBtn = document.getElementById('modal-search-btn');
    const modalSearchInput = document.getElementById('modal-book-search');
    const modalResults = document.getElementById('modal-search-results');

    async function doModalSearch() {
      const q = modalSearchInput.value.trim();
      if (!q) return;
      modalResults.innerHTML = '<div style="padding:8px;color:var(--text-muted);font-size:0.82rem;">Searching…</div>';
      try {
        const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}&max_results=8`);
        const data = await safeJson(res);
        if (!data.books || !data.books.length) {
          modalResults.innerHTML = '<div style="padding:8px;color:var(--text-muted);font-size:0.82rem;">No results found.</div>';
          return;
        }
        modalResults.innerHTML = '';
        data.books.forEach(book => {
          const item = document.createElement('div');
          item.className = 'modal-result-item';
          item.innerHTML = `
            ${book.thumbnail ? `<img src="${book.thumbnail}" alt="" class="modal-result-thumb">` : ''}
            <div class="modal-result-info">
              <div class="modal-result-title">${book.title}</div>
              ${book.authors ? `<div class="modal-result-author">${book.authors}</div>` : ''}
            </div>`;
          item.addEventListener('click', () => prefillForm(book));
          modalResults.appendChild(item);
        });
      } catch (e) {
        modalResults.innerHTML = '<div style="padding:8px;color:var(--text-muted);font-size:0.82rem;">Search failed.</div>';
      }
    }

    if (modalSearchBtn) modalSearchBtn.addEventListener('click', doModalSearch);
    if (modalSearchInput) modalSearchInput.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); doModalSearch(); } });

    function prefillForm(book) {
      document.getElementById('f-title').value      = book.title || '';
      document.getElementById('f-authors').value    = book.authors || '';
      document.getElementById('f-thumbnail').value  = book.thumbnail || '';
      document.getElementById('f-google-books-id').value = book.google_books_id || '';
      document.getElementById('f-published-date').value  = book.published_date || '';
      document.getElementById('f-categories').value      = book.categories || '';

      const sel = document.getElementById('form-selected-book');
      const thumb = document.getElementById('form-selected-thumb');
      document.getElementById('form-selected-title').textContent   = book.title;
      document.getElementById('form-selected-authors').textContent = book.authors || '';
      if (book.thumbnail) { thumb.src = book.thumbnail; thumb.style.display = ''; }
      else thumb.style.display = 'none';
      sel.style.display = '';

      if (!coverDataUrl && book.thumbnail) {
        setCoverPreview(book.thumbnail);
      }

      stepPick.style.display = 'none';
      stepForm.style.display = '';
    }

    // Submit form
    const addForm = document.getElementById('add-book-form');
    if (addForm) {
      addForm.addEventListener('submit', async e => {
        e.preventDefault();
        const title = document.getElementById('f-title').value.trim();
        const ownerName = document.getElementById('f-owner-name').value.trim();
        if (!title) { toast('Book title is required.', 'error'); return; }
        if (!ownerName) { toast('Your name is required.', 'error'); return; }

        const btn = document.getElementById('btn-submit-book');
        btn.disabled = true;
        btn.textContent = 'Listing…';

        const thumbnailValue = coverDataUrl || document.getElementById('f-thumbnail').value.trim();

        const payload = {
          title,
          authors:         document.getElementById('f-authors').value.trim(),
          owner_name:      ownerName,
          owner_contact:   document.getElementById('f-owner-contact').value.trim(),
          location:        document.getElementById('f-location').value.trim(),
          condition:       document.getElementById('f-condition').value,
          notes:           document.getElementById('f-notes').value.trim(),
          thumbnail:       thumbnailValue,
          google_books_id: document.getElementById('f-google-books-id').value.trim(),
          published_date:  document.getElementById('f-published-date').value.trim(),
          categories:      document.getElementById('f-categories').value.trim(),
          listing_type:    (document.querySelector('input[name="f-listing-type"]:checked') || {}).value || 'borrow',
        };

        try {
          const res = await fetch('/api/community/add/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          const data = await safeJson(res);
          if (!res.ok) throw new Error(data.error || 'Failed to list book.');

          try {
            const updatedIds = await sessionAddMyBook(data.book.id);
            const badge = document.getElementById('my-books-badge');
            if (badge && updatedIds.length > 0) { badge.textContent = updatedIds.length; badge.style.display = ''; }
          } catch(e) {}

          toast('Book listed! Others can now see and borrow it. 📚');
          closeModal();
          await loadBooks(searchInput ? searchInput.value.trim() : '');
        } catch (err) {
          toast(err.message, 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'List Book';
        }
      });
    }
  }


  // ══════════════════════════════════════════════════════════════════════
  // COMMUNITY BOOK DETAIL PAGE
  // ══════════════════════════════════════════════════════════════════════
  const bookId = window.COMMUNITY_BOOK_ID;
  if (bookId) {
    // Load borrow requests
    async function loadRequests() {
      try {
        const res = await fetch(`/api/community/${bookId}/`);
        const data = await safeJson(res);
        const requests = (data.book || {}).borrow_requests || [];
        if (!requests.length) return;

        const section = document.getElementById('borrow-requests-section');
        const list = document.getElementById('borrow-requests-list');
        if (!section || !list) return;

        // Only show borrow requests panel if the current user is the book owner
        let isOwner = false;
        try {
          const myBooks = await sessionGetMyBooks();
          isOwner = myBooks.includes(bookId);
        } catch(e) {}

        if (!isOwner) return;  // Visitors / requesters cannot see or action requests

        section.style.display = '';
        list.innerHTML = '';
        requests.forEach(req => {
          const card = document.createElement('div');
          card.className = 'borrow-request-card';
          card.innerHTML = `
            <div class="borrow-req-header">
              <div class="borrow-req-name">${req.requester_name}</div>
              <span class="status-pill ${statusClass(req.status)}">${req.status_display}</span>
            </div>
            <div class="borrow-req-contact">${req.requester_contact}</div>
            ${req.message ? `<div class="borrow-req-message">"${req.message}"</div>` : ''}
            <div class="borrow-req-actions">
              ${req.status === 'pending' ? `
                <button class="btn-approve" data-id="${req.id}" data-action="approved">Approve</button>
                <button class="btn-decline" data-id="${req.id}" data-action="declined">Decline</button>
              ` : ''}
              ${req.status === 'approved' ? `
                <button class="btn-returned" data-id="${req.id}" data-action="returned">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.5"/>
                  </svg>
                  Mark as Returned
                </button>
              ` : ''}
              ${req.status === 'returned' ? `
                <span class="return-badge">✓ Returned</span>
              ` : ''}
            </div>`;
          list.appendChild(card);
        });

        list.addEventListener('click', async e => {
          const btn = e.target.closest('[data-action]');
          if (!btn) return;
          const reqId = btn.dataset.id;
          const action = btn.dataset.action;
          btn.disabled = true;

          const origText = btn.textContent;
          btn.textContent = action === 'returned' ? 'Updating…' : origText;

          try {
            const res = await fetch(`/api/community/requests/${reqId}/status/`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ status: action }),
            });
            const data = await safeJson(res);
            if (!res.ok) throw new Error(data.error || 'Update failed.');

            const msgs = {
              approved: 'Request approved! The book is now marked as borrowed. 📖',
              declined: 'Request declined.',
              returned: 'Book marked as returned and available again! 🎉',
            };
            toast(msgs[action] || `Request ${action}.`);
            setTimeout(() => location.reload(), 900);
          } catch (err) {
            toast(err.message, 'error');
            btn.disabled = false;
            btn.textContent = origText;
          }
        });
      } catch (e) {
        // Silently fail — borrow requests are optional to display
      }
    }
    loadRequests();

    // ── Borrow Modal ──
    const borrowModal = document.getElementById('borrow-modal');
    const openBorrowBtn = document.getElementById('open-borrow-modal');
    const closeBorrowBtn = document.getElementById('close-borrow-modal');
    const cancelBorrowBtn = document.getElementById('cancel-borrow');

    if (openBorrowBtn) openBorrowBtn.addEventListener('click', () => { borrowModal.style.display = 'flex'; });
    if (closeBorrowBtn) closeBorrowBtn.addEventListener('click', () => { borrowModal.style.display = 'none'; });
    if (cancelBorrowBtn) cancelBorrowBtn.addEventListener('click', () => { borrowModal.style.display = 'none'; });
    if (borrowModal) borrowModal.addEventListener('click', e => { if (e.target === borrowModal) borrowModal.style.display = 'none'; });

    const borrowForm = document.getElementById('borrow-form');
    if (borrowForm) {
      borrowForm.addEventListener('submit', async e => {
        e.preventDefault();
        const name    = document.getElementById('b-name').value.trim();
        const contact = document.getElementById('b-contact').value.trim();
        const message = document.getElementById('b-message').value.trim();
        const meetupDatetime = document.getElementById('b-meetup-datetime').value || null;

        if (!name)    { toast('Your name is required.', 'error'); return; }
        if (!contact) { toast('Your contact info is required.', 'error'); return; }

        const requestType = (document.querySelector('input[name="b-request-type"]:checked') || {}).value || 'borrow';

        const submitBtn = borrowForm.querySelector('[type=submit]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending…';

        try {
          const res = await fetch(`/api/community/${bookId}/borrow/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ requester_name: name, requester_contact: contact, message, meetup_datetime: meetupDatetime, request_type: requestType }),
          });
          const data = await safeJson(res);
          if (!res.ok) throw new Error(data.error || 'Failed to send request.');
          toast('Borrow request sent! The owner will get in touch with you. 🎉');
          borrowModal.style.display = 'none';
          borrowForm.reset();
          // Save this request ID so the requester can track/edit/cancel it
          try {
            if (data.request && data.request.id) {
              const updatedIds = await sessionAddMyRequest(data.request.id);
              const rbadge = document.getElementById('my-requests-badge');
              if (rbadge && updatedIds.length > 0) { rbadge.textContent = updatedIds.length; rbadge.style.display = ''; }
            }
          } catch(e) {}
        } catch (err) {
          toast(err.message, 'error');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Send Request';
        }
      });
    }

    // ── Owner Actions (Edit / Delete) ──
    (async function() {
      try {
        const myBooks = await sessionGetMyBooks();
        if (myBooks.includes(bookId)) {
          const ownerActions = document.getElementById('owner-actions');
          if (ownerActions) ownerActions.style.display = '';
          const borrowCta = document.getElementById('borrow-cta');
          if (borrowCta) borrowCta.style.display = 'none';
        }
      } catch(e) {}
    })();

    // Edit modal open/close
    const editModal     = document.getElementById('edit-modal');
    const openEditBtn   = document.getElementById('open-edit-modal');
    const closeEditBtn  = document.getElementById('close-edit-modal');
    const cancelEditBtn = document.getElementById('cancel-edit');

    if (openEditBtn)   openEditBtn.addEventListener('click', () => { editModal.style.display = 'flex'; });
    if (closeEditBtn)  closeEditBtn.addEventListener('click', () => { editModal.style.display = 'none'; });
    if (cancelEditBtn) cancelEditBtn.addEventListener('click', () => { editModal.style.display = 'none'; });
    if (editModal)     editModal.addEventListener('click', e => { if (e.target === editModal) editModal.style.display = 'none'; });

    // Edit form submit
    const editForm = document.getElementById('edit-form');
    if (editForm) {
      editForm.addEventListener('submit', async e => {
        e.preventDefault();
        const submitBtn = editForm.querySelector('[type=submit]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving…';

        const payload = {
          condition:     document.getElementById('e-condition').value,
          notes:         document.getElementById('e-notes').value.trim(),
          location:      document.getElementById('e-location').value.trim(),
          owner_contact: document.getElementById('e-owner-contact').value.trim(),
          is_available:  document.getElementById('e-available').checked,
          listing_type:  (document.querySelector('input[name="e-listing-type"]:checked') || {}).value || 'borrow',
        };

        try {
          const res = await fetch(`/api/community/${bookId}/update/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          const data = await safeJson(res);
          if (!res.ok) throw new Error(data.error || 'Update failed.');
          toast('Book listing updated! ✅');
          editModal.style.display = 'none';
          setTimeout(() => location.reload(), 700);
        } catch (err) {
          toast(err.message, 'error');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Save Changes';
        }
      });
    }

    // Delete button
    const deleteBtn = document.getElementById('delete-book-btn');
    if (deleteBtn) {
      deleteBtn.addEventListener('click', async () => {
        if (!confirm('Remove this book listing permanently? This cannot be undone.')) return;
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting…';
        try {
          const res = await fetch(`/api/community/${bookId}/delete/`, { method: 'DELETE' });
          if (!res.ok) { const d = await res.json(); throw new Error(d.error || 'Delete failed.'); }
          try {
            await sessionRemoveMyBook(bookId);
          } catch(e) {}
          toast('Book listing removed.');
          setTimeout(() => { window.location.href = '/community/'; }, 900);
        } catch (err) {
          toast(err.message, 'error');
          deleteBtn.disabled = false;
          deleteBtn.textContent = 'Delete Listing';
        }
      });
    }
  }


  // ══════════════════════════════════════════════════════════════════════
  // MY BOOKS PAGE
  // ══════════════════════════════════════════════════════════════════════
  const myBooksGrid = document.getElementById('my-books-grid');
  if (myBooksGrid) {
    const myBooksLoading = document.getElementById('my-books-loading');
    const myBooksEmpty   = document.getElementById('my-books-empty');
    const myBooksStats   = document.getElementById('my-books-stats');

    async function loadMyBooks() {
      let myBookIds = [];
      try { myBookIds = await sessionGetMyBooks(); } catch(e) {}

      if (!myBookIds.length) {
        if (myBooksLoading) myBooksLoading.style.display = 'none';
        if (myBooksEmpty) myBooksEmpty.style.display = '';
        return;
      }

      try {
        const res = await fetch('/api/community/');
        const data = await safeJson(res);
        const books = (data.books || []).filter(b => myBookIds.includes(b.id));

        // Sync session: remove stale IDs
        const validIds = books.map(b => b.id);
        const staleRemoved = myBookIds.filter(id => !validIds.includes(id));
        if (staleRemoved.length) {
          for (const staleId of staleRemoved) { await sessionRemoveMyBook(staleId); }
          const badge = document.getElementById('my-books-badge');
          if (badge) {
            if (validIds.length > 0) { badge.textContent = validIds.length; badge.style.display = ''; }
            else badge.style.display = 'none';
          }
        }

        if (myBooksLoading) myBooksLoading.style.display = 'none';

        if (!books.length) {
          if (myBooksEmpty) myBooksEmpty.style.display = '';
          return;
        }

        if (myBooksStats) {
          const avail = books.filter(b => b.is_available).length;
          myBooksStats.textContent = `${books.length} book${books.length !== 1 ? 's' : ''} listed · ${avail} available`;
        }

        myBooksGrid.innerHTML = '';
        myBooksGrid.style.display = '';

        books.forEach(book => {
          const card = document.createElement('div');
          card.className = 'community-card my-book-card';
          const chip = book.is_available
            ? '<span class="availability-chip available">Available</span>'
            : '<span class="availability-chip unavailable">Borrowed</span>';
          card.innerHTML = `
            <a href="/community/${book.id}/" class="my-book-card-inner">
              <div class="community-card-cover">
                ${coverHTML(book)}
                ${chip}
              </div>
              <div class="community-card-body">
                <div class="community-card-title">${book.title}</div>
                ${book.authors ? `<div class="community-card-author">${book.authors}</div>` : ''}
                <div class="community-card-footer">
                  <div class="community-card-owner">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                    </svg>
                    ${book.owner_name}
                  </div>
                  <span class="condition-badge condition-${book.condition}">${conditionLabel(book.condition)}</span>
                </div>
              </div>
            </a>
            <div class="my-book-actions">
              <a href="/community/${book.id}/" class="btn-outline btn-sm">View</a>
              <button class="btn-danger btn-sm" data-delete="${book.id}">Remove</button>
            </div>`;
          myBooksGrid.appendChild(card);
        });

        // Delete from My Books page
        myBooksGrid.addEventListener('click', async e => {
          const btn = e.target.closest('[data-delete]');
          if (!btn) return;
          const id = parseInt(btn.dataset.delete);
          if (!confirm('Remove this book listing permanently?')) return;
          btn.disabled = true;
          btn.textContent = '…';
          try {
            const res = await fetch(`/api/community/${id}/delete/`, { method: 'DELETE' });
            if (!res.ok) { const d = await res.json(); throw new Error(d.error || 'Delete failed.'); }
            const updated = await sessionRemoveMyBook(id);
            const badge = document.getElementById('my-books-badge');
            if (badge) {
              if (updated.length > 0) { badge.textContent = updated.length; badge.style.display = ''; }
              else badge.style.display = 'none';
            }
            toast('Book listing removed.');
            btn.closest('.my-book-card').remove();
            if (!myBooksGrid.children.length) {
              myBooksGrid.style.display = 'none';
              if (myBooksEmpty) myBooksEmpty.style.display = '';
              if (myBooksStats) myBooksStats.textContent = 'No books listed.';
            }
          } catch(err) {
            toast(err.message, 'error');
            btn.disabled = false;
            btn.textContent = 'Remove';
          }
        });

      } catch(e) {
        if (myBooksLoading) myBooksLoading.style.display = 'none';
        toast('Could not load your books.', 'error');
      }
    }
    loadMyBooks();
  }

})();