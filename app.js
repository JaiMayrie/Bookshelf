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
if (bookList) {
  const books = getBooks();
  if (books.length === 0) {
    bookList.innerHTML = '<p>No books found. <a href="upload.html">Add some books</a>.</p>';
  } else {
    bookList.innerHTML = books.map(book => `
      <div class="book-item">
        <h3>${book.title}</h3>
        <p><strong>Author:</strong> ${book.author}</p>
        <p><strong>Genre:</strong> ${book.genre}</p>
        <p>${book.description || ''}</p>
      </div>
    `).join('');
  }
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

// Search functionality
const searchInput = document.getElementById('search-input');
if (searchInput) {
  searchInput.addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    const books = getBooks();
    const filtered = books.filter(book => 
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query) ||
      book.genre.toLowerCase().includes(query)
    );
    
    const bookList = document.getElementById('book-list');
    if (bookList) {
      if (filtered.length === 0) {
        bookList.innerHTML = '<p>No books match your search.</p>';
      } else {
        bookList.innerHTML = filtered.map(book => `
          <div class="book-item">
            <h3>${book.title}</h3>
            <p><strong>Author:</strong> ${book.author}</p>
            <p><strong>Genre:</strong> ${book.genre}</p>
            <p>${book.description || ''}</p>
          </div>
        `).join('');
      }
    }
  });
}
