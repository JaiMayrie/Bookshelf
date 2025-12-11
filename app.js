// Minimal client-side wiring for Browse and Book pages
async function fetchJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error('Network error');
  return res.json();
}

document.addEventListener('DOMContentLoaded', () => {
  // Login form: validate and submit with inline error display
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const username = loginForm.querySelector('#login-username').value.trim();
      const password = loginForm.querySelector('#login-password').value.trim();
      const errorDiv = document.getElementById('login-error');

      if (!username || !password) {
        errorDiv.textContent = 'Username and password are required.';
        errorDiv.style.display = 'block';
        return;
      }

      const fd = new FormData(loginForm);
      fetch('/login', { method: 'POST', body: fd })
        .then(r => {
          if (r.redirected) {
            window.location = r.url;
            return;
          }
          if (!r.ok) return r.text().then(msg => { throw new Error(msg); });
          return r.text().then(() => { window.location = '/home.html'; });
        })
        .catch(err => {
          errorDiv.textContent = err.message || 'Login failed. Please try again.';
          errorDiv.style.display = 'block';
        });
    });
  }

  // Register form: validate and submit with inline error display
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', (ev) => {
      ev.preventDefault();
      const username = registerForm.querySelector('#reg-username').value.trim();
      const password = registerForm.querySelector('#reg-password').value.trim();
      const confirmPassword = registerForm.querySelector('#reg-confirm-password').value.trim();
      const errorDiv = document.getElementById('register-error');

      if (!username || !password || !confirmPassword) {
        errorDiv.textContent = 'All fields are required.';
        errorDiv.style.display = 'block';
        return;
      }

      if (password !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match.';
        errorDiv.style.display = 'block';
        return;
      }

      const fd = new FormData(registerForm);
      fetch('/register', { method: 'POST', body: fd })
        .then(r => {
          if (r.redirected) {
            window.location = r.url;
            return;
          }
          if (!r.ok) return r.text().then(msg => { throw new Error(msg); });
          return r.text().then(() => { window.location = '/home.html'; });
        })
        .catch(err => {
          errorDiv.textContent = err.message || 'Registration failed. Please try again.';
          errorDiv.style.display = 'block';
        });
    });
  }

  // Browse page: populate results table if present
  const resultsTable = document.getElementById('results-table');
  if (resultsTable) {
    const tbody = resultsTable.querySelector('tbody');
    function renderBooksList(list) {
      tbody.innerHTML = '';
      if (!list || !list.length) {
        tbody.innerHTML = '<tr><td colspan="5">No books available.</td></tr>';
        return;
      }
      list.forEach(b => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><a href="book.html?id=${encodeURIComponent(b.id)}" class="title-link" data-id="${b.id}" data-file="${escapeHtml(b.file_path || '')}">${escapeHtml(b.title || '')}</a></td>
          <td>${escapeHtml(b.author || '')}</td>
          <td>${escapeHtml(b.genre || '')}</td>
          <td>${escapeHtml((b.keywords || []).join(', '))}</td>
          <td><button data-id="${b.id}" class="add-btn">Add</button></td>
        `;
        tbody.appendChild(tr);
      });
    }

    // initial load
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';
    function fetchAndRender(query) {
      const path = query ? '/api/books' + (query.startsWith('?') ? query : ('?' + query)) : '/api/books';
      console.log('[Browse] fetchAndRender called with path:', path);
      fetch(path)
        .then(res => {
          console.log('[Browse] Fetch response status:', res.status);
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
          }
          return res.json();
        })
        .then(list => {
          console.log('[Browse] Received list from API:', list, 'Length:', list ? list.length : 'null');
          renderBooksList(list);
        })
        .catch(err => {
          console.error('[Browse] Error fetching books:', err);
          tbody.innerHTML = '<tr><td colspan="5">Error loading books: ' + err.message + '</td></tr>';
        });
    }
    console.log('[Browse] Page loaded, table element found, calling fetchAndRender');
    fetchAndRender('');

    // delegated handler for Add buttons
    resultsTable.addEventListener('click', (ev) => {
      const btn = ev.target.closest && ev.target.closest('.add-btn');
      if (!btn) return;
      const bookId = btn.getAttribute('data-id');
      if (!bookId) return;
      btn.disabled = true;
      const fd = new FormData(); fd.append('book_id', bookId);
      fetch('/api/bookshelf/add', { method: 'POST', body: fd }).then(r => r.json()).then(() => {
        btn.textContent = 'Added';
      }).catch(e => {
        console.error(e);
        btn.disabled = false;
        btn.textContent = 'Add';
      });
    });

    // wire search form (if present) to query the API and re-render
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
      searchForm.addEventListener('submit', (ev) => {
          ev.preventDefault();
          const form = ev.target;
          const title = (form.querySelector('[name="title"]') || {value:''}).value.trim();
          const author = (form.querySelector('[name="author"]') || {value:''}).value.trim();
          const keywords = (form.querySelector('[name="keywords"]') || {value:''}).value.trim();
          const genre = (form.querySelector('[name="genre"]') || {value:''}).value.trim();

          const params = new URLSearchParams();
          // server expects `keyword` (or `keywords`) for token scoring; combine title+keywords
          let kwParam = '';
          if (title) kwParam = title;
          if (keywords) kwParam = kwParam ? (kwParam + ' ' + keywords) : keywords;
          if (kwParam) params.set('keyword', kwParam);
          if (genre) params.set('genre', genre);
          if (author) params.set('author', author);
          fetchAndRender('?' + params.toString());
        });
    }
  }

  // Book page: fetch book by id in querystring
  const titleDisplay = document.getElementById('book-title-display');
  if (titleDisplay) {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (id) {
      fetchJSON('/api/book/' + encodeURIComponent(id)).then(b => {
        titleDisplay.textContent = b.title || 'Book Title';
        const authorEl = document.getElementById('book-author-display');
        const genreEl = document.getElementById('book-genre-display');
        const keywordsEl = document.getElementById('book-keywords-display');
        if (authorEl) authorEl.textContent = b.author || '';
        if (genreEl) genreEl.textContent = b.genre || '';
        if (keywordsEl) keywordsEl.textContent = (b.keywords || []).join(', ');

        const pdfViewer = document.getElementById('pdf-viewer');
        const canvasContainer = document.getElementById('pdf-canvas-container');
        const limitedNote = document.getElementById('limited-note');

        function _fullUrl(path) {
          if (!path) return null;
          return path.startsWith('/') ? path : '/' + path;
        }

        // check whether current user has this book in their bookshelf
        fetch('/api/bookshelf/check/' + encodeURIComponent(id)).then(r => r.json()).then(stat => {
          const inShelf = stat && stat.in_shelf;
          const url = _fullUrl(b.file_path);
          if (inShelf) {
            // show full iframe
            if (canvasContainer) canvasContainer.innerHTML = '';
            if (limitedNote) limitedNote.textContent = '';
            if (pdfViewer && url) {
              pdfViewer.style.display = 'block';
              pdfViewer.src = url + '#page=1';
            }
          } else {
            // render only first few pages using PDF.js
            if (pdfViewer) pdfViewer.style.display = 'none';
            if (limitedNote) limitedNote.textContent = 'Preview: only the first 3 pages are shown. Add to your bookshelf to view the full book.';
            if (canvasContainer && url && window.pdfjsLib) {
              renderFirstPages(url, 3, canvasContainer);
            } else if (canvasContainer && url) {
              // fallback: show first page via iframe if PDF.js not available
              canvasContainer.innerHTML = '<iframe src="' + url + '#page=1" style="width:100%; height:400px; border:1px solid #ccc;"></iframe>';
            }
          }

          // wire add/remove buttons to toggle bookshelf membership
          const addBtn = document.getElementById('add-to-bookshelf-btn');
          const removeBtn = document.getElementById('remove-from-bookshelf-btn');
          if (addBtn) {
            addBtn.style.display = inShelf ? 'none' : 'inline-block';
            addBtn.onclick = () => {
              const fd = new FormData(); fd.append('book_id', id);
              fetch('/api/bookshelf/add', {method:'POST', body:fd}).then(r=>r.json()).then(() => {
                // after adding, show full iframe
                if (pdfViewer && url) { pdfViewer.style.display='block'; pdfViewer.src = url + '#page=1'; }
                if (canvasContainer) canvasContainer.innerHTML = '';
                if (limitedNote) limitedNote.textContent = '';
                addBtn.style.display = 'none';
                if (removeBtn) removeBtn.style.display = 'inline-block';
              }).catch(err=>console.error(err));
            };
          }
          if (removeBtn) {
            removeBtn.style.display = inShelf ? 'inline-block' : 'none';
            removeBtn.onclick = () => {
              const fd = new FormData(); fd.append('book_id', id);
              fetch('/api/bookshelf/remove', {method:'POST', body:fd}).then(r=>r.json()).then(() => {
                // after removing, render limited preview
                if (pdfViewer) pdfViewer.style.display='none';
                if (limitedNote) limitedNote.textContent = 'Preview: only the first 3 pages are shown. Add to your bookshelf to view the full book.';
                if (canvasContainer && b.file_path && window.pdfjsLib) renderFirstPages(_fullUrl(b.file_path), 3, canvasContainer);
                removeBtn.style.display = 'none';
                if (addBtn) addBtn.style.display = 'inline-block';
              }).catch(err=>console.error(err));
            };
          }
        }).catch(err => console.error(err));
      }).catch(err => console.error(err));
    }
  }

  // Bookshelf page: render the current user's saved books
  const shelfContainer = document.getElementById('bookshelf-list');
  if (shelfContainer) {
    fetchJSON('/api/bookshelf').then(list => {
      shelfContainer.innerHTML = '';
      if (!list.length) {
        shelfContainer.innerHTML = '<p>Your bookshelf is empty.</p>';
        return;
      }
      list.forEach(b => {
        const card = document.createElement('article');
        card.className = 'book-card';
        card.innerHTML = `
          <h2><a href="book.html?id=${b.id}">${escapeHtml(b.title || '')}</a></h2>
          <p>Author: ${escapeHtml(b.author || '')}</p>
          <p>Genre: ${escapeHtml(b.genre || '')}</p>
          <p>Keywords: ${escapeHtml((b.keywords || []).join(', '))}</p>
          <div class="book-card-actions">
            <button class="remove-btn">Remove from Bookshelf</button>
          </div>
        `;
        const removeBtn = card.querySelector('.remove-btn');
        removeBtn.addEventListener('click', () => {
          const fd = new FormData(); fd.append('book_id', b.id);
          fetch('/api/bookshelf/remove', { method: 'POST', body: fd }).then(r => r.json()).then(() => {
            card.remove();
            // if container is empty now, show empty message
            if (!shelfContainer.querySelector('.book-card')) shelfContainer.innerHTML = '<p>Your bookshelf is empty.</p>';
          }).catch(err => console.error(err));
        });
        shelfContainer.appendChild(card);
      });
    }).catch(err => {
      console.error(err);
      shelfContainer.innerHTML = '<p>Unable to load bookshelf.</p>';
    });
  }
});

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Render first `count` pages of a PDF at `url` into `container` using PDF.js
function renderFirstPages(url, count, container) {
  try {
    const pdfjsLib = window.pdfjsLib || window['pdfjs-dist/build/pdf'];
    if (!pdfjsLib) throw new Error('pdfjs not loaded');
    // set workerSrc to CDN
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
    container.innerHTML = '';
    const loadingTask = pdfjsLib.getDocument(url);
    loadingTask.promise.then(pdf => {
      const max = Math.min(count, pdf.numPages);
      for (let p = 1; p <= max; p++) {
        pdf.getPage(p).then(page => {
          const scale = 1.2;
          const viewport = page.getViewport({ scale });
          const canvas = document.createElement('canvas');
          canvas.style.display = 'block';
          canvas.style.marginBottom = '8px';
          const ctx = canvas.getContext('2d');
          canvas.width = viewport.width;
          canvas.height = viewport.height;
          container.appendChild(canvas);
          const renderContext = {
            canvasContext: ctx,
            viewport: viewport
          };
          page.render(renderContext);
        });
      }
    }).catch(err => {
      console.error('Error loading PDF:', err);
      container.innerHTML = '<p>Unable to load preview.</p>';
    });
  } catch (e) {
    console.error(e);
    container.innerHTML = '<p>PDF preview unavailable.</p>';
  }
}
