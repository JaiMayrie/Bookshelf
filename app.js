// Book Organizer App

// Simple local storage for demo purposes
const BOOKS_KEY = 'bookOrganizer_books';
const USER_KEY = 'bookOrganizer_user';

// Get books from local storage
function getBooks() {
  const books = localStorage.getItem(BOOKS_KEY);
  return books ? JSON.parse(books) : [];
}

// Save books to local storage
function saveBooks(books) {
  localStorage.setItem(BOOKS_KEY, JSON.stringify(books));
}

// Add a new book
function addBook(book) {
  const books = getBooks();
  book.id = Date.now();
  books.push(book);
  saveBooks(books);
  return book;
}

// Handle login form
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    localStorage.setItem(USER_KEY, username);
    alert('Logged in as ' + username);
    window.location.href = 'home.html';
  });
}

// Handle register form
const registerForm = document.getElementById('register-form');
if (registerForm) {
  registerForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    localStorage.setItem(USER_KEY, username);
    alert('Registered and logged in as ' + username);
    window.location.href = 'home.html';
  });
}

// Handle upload form
const uploadForm = document.getElementById('upload-form');
if (uploadForm) {
  uploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const book = {
      title: document.getElementById('book-title').value,
      author: document.getElementById('book-author').value,
      genre: document.getElementById('book-genre').value,
      description: document.getElementById('book-description').value
    };
    addBook(book);
    alert('Book added successfully!');
    uploadForm.reset();
  });
}

// Display books on browse page
const bookList = document.getElementById('book-list');
const noResults = document.getElementById('no-results');
const resultsCount = document.getElementById('results-count');

function displayBooks(books) {
  if (!bookList) return;
  
  if (books.length === 0) {
    bookList.innerHTML = '';
    if (noResults) noResults.style.display = 'block';
    if (resultsCount) resultsCount.textContent = '';
  } else {
    if (noResults) noResults.style.display = 'none';
    if (resultsCount) resultsCount.textContent = `${books.length} book${books.length !== 1 ? 's' : ''} found`;
    bookList.innerHTML = books.map(book => `
      <div class="book-item">
        <h3>${book.title}</h3>
        <p><strong>Author:</strong> ${book.author}</p>
        <span class="genre-tag">${book.genre}</span>
        <p>${book.description || ''}</p>
      </div>
    `).join('');
  }
}

if (bookList) {
  displayBooks(getBooks());
}

// Display bookshelf
const bookshelfList = document.getElementById('bookshelf-list');
if (bookshelfList) {
  const books = getBooks();
  if (books.length === 0) {
    bookshelfList.innerHTML = '<p>Your bookshelf is empty. <a href="upload.html">Add some books</a>.</p>';
  } else {
    bookshelfList.innerHTML = books.map(book => `
      <div class="book-item">
        <h3>${book.title}</h3>
        <p><strong>Author:</strong> ${book.author}</p>
        <p><strong>Genre:</strong> ${book.genre}</p>
        <button onclick="removeBook(${book.id})">Remove</button>
      </div>
    `).join('');
  }
}

// Remove book
function removeBook(id) {
  let books = getBooks();
  books = books.filter(b => b.id !== id);
  saveBooks(books);
  location.reload();
}

// Search form functionality for browse page
const searchForm = document.getElementById('search-form');
if (searchForm) {
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const keyword = document.getElementById('search-keyword').value.toLowerCase();
    const genre = document.getElementById('search-genre').value;
    
    const books = getBooks();
    const filtered = books.filter(book => {
      const matchesKeyword = !keyword || 
        book.title.toLowerCase().includes(keyword) ||
        book.author.toLowerCase().includes(keyword) ||
        (book.description && book.description.toLowerCase().includes(keyword));
      
      const matchesGenre = !genre || book.genre === genre;
      
      return matchesKeyword && matchesGenre;
    });
    
    displayBooks(filtered);
  });
  
  // Live search as user types
  const searchKeyword = document.getElementById('search-keyword');
  const searchGenre = document.getElementById('search-genre');
  
  if (searchKeyword) {
    searchKeyword.addEventListener('input', function() {
      searchForm.dispatchEvent(new Event('submit'));
    });
  }
  
  if (searchGenre) {
    searchGenre.addEventListener('change', function() {
      searchForm.dispatchEvent(new Event('submit'));
    });
  }
}
