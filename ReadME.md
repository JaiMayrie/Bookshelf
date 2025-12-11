# Bookshelf Application

A Flask-based web application for managing, browsing, and reading books with user authentication and personal bookshelves.

## Features

- **User Authentication**: Register and login with persistent credentials stored in `users.json` and `logininfo.txt`.
- **Book Upload**: Upload PDF books with metadata (title, author, genre, keywords).
- **Browse Library**: Search and filter books by keyword (scored by relevance), author, or genre.
- **Personal Bookshelf**: Add books to your personal bookshelf to unlock full PDF reading access.
- **PDF Viewing**: 
  - Full access for books in your bookshelf (scrollable PDF viewer).
  - Preview (first 3 pages) for books not yet in your bookshelf.
- **Responsive Design**: Simple, clean HTML and CSS interface.

## Prerequisites

- Python 3.7+
- Flask 2.0+
- PDF.js (loaded from CDN, no installation needed for preview)

## Setup & Installation

### 1. Install Dependencies

From the `Bookshelf/` directory (where `server.py` is located), run:

```powershell
pip install -r requirements.txt
```

Or manually install:

```powershell
pip install Flask>=2.0
```

### 2. Directory Structure

Ensure the project folder has this structure:

```
Bookshelf/
├── server.py              # Flask application
├── book_logic.py          # Book and bookshelf logic
├── app.js                 # Client-side JavaScript
├── requirements.txt       # Python dependencies
├── bookvals.txt           # Stores book metadata (created automatically)
├── users.json             # User registration data (created on first register)
├── logininfo.txt          # User login credentials (created on first login)
├── usershelves.json       # Per-user bookshelf data (created on first add)
├── books/                 # Uploaded PDF files (created on first upload)
│   └── (PDF files here)
├── *.html                 # HTML pages (home.html, login.html, register.html, etc.)
├── styles.css             # CSS styles
└── Browse.html            # Redirect to browse.html
```

## Startup Procedure

### Step 1: Open Terminal

Navigate to the `Bookshelf/` directory:

```powershell
cd c:\Users\tombe\Bookshelf\Bookshelf
```

### Step 2: Start the Flask Server

Run the server in debug mode:

```powershell
python server.py
```

You should see output like:

```
 * Serving Flask app 'server'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 3: Open in Browser

Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

You will be redirected to the login page (because no session exists).

### Step 4: Register a New Account

1. Click **"Create an Account"** link or navigate to `/register.html`.
2. Enter a username and password.
3. Click **Register**.
4. You will be logged in and redirected to the home page.

### Step 5: Upload a Book (Optional)

1. Click **"Add Book"** in the navigation menu.
2. Select a PDF file from your computer.
3. Enter book metadata:
   - **Title**: Book name
   - **Author**: Author name
   - **Genre**: Select from dropdown (Fantasy, Romance, Mystery, Non-Fiction)
   - **Keywords**: Comma-separated tags (e.g., "magic, adventure")
4. Click **Upload Book**.
5. You will be redirected to your bookshelf (book now added automatically).

### Step 6: Browse Books

1. Click **"Browse"** in the navigation menu.
2. Use the search form to filter by:
   - **Keyword**: Searches title, author, and keywords. Results are scored by match count.
   - **Genre**: Filter by book genre.
   - **Author**: Filter by author name.
3. Click a book title to view its details.
4. Click **"Add to Bookshelf"** to unlock full PDF access.

### Step 7: View Your Bookshelf

1. Click **"My Bookshelf"** in the navigation menu.
2. See all books you've added.
3. Click a book title to view it.
4. Click **"Remove from Bookshelf"** to remove a book.

### Step 8: Read a Book

1. From Browse or Bookshelf, click a book title.
2. If the book is **in your bookshelf**:
   - Full PDF viewer loads with all pages.
   - Use the PDF viewer controls to scroll and navigate.
3. If the book is **not in your bookshelf**:
   - First 3 pages render as a preview.
   - Click **"Add to Bookshelf"** to unlock full access.

## File Descriptions

| File | Purpose |
|------|---------|
| `server.py` | Main Flask application with all routes and endpoints. |
| `book_logic.py` | Core classes: `user`, `reader`, `uploader`, `bookshelf`, `book`. |
| `app.js` | Client-side JavaScript for Browse, Book, and Bookshelf pages. |
| `bookvals.txt` | Newline-delimited JSON storing all uploaded book metadata. |
| `users.json` | JSON mapping of username → {password} for registration. |
| `logininfo.txt` | JSON mapping of username → {password} for login/authentication. |
| `usershelves.json` | JSON mapping of username → [book_id_list] for personal bookshelves. |
| `books/` | Directory containing uploaded PDF files. |
| `*.html` | Static HTML pages (home, login, register, browse, book, bookshelf, upload). |

## API Endpoints

### Public (No Login Required)

- `GET /login.html` - Login page.
- `GET /register.html` - Registration page.
- `POST /login` - Handle login (expects `username`, `password`).
- `POST /register` - Handle registration (expects `username`, `password`).

### Protected (Login Required)

- `GET /` - Home page (redirects to login if not authenticated).
- `GET /home.html` - Home page.
- `GET /browse.html` - Browse books page.
- `GET /book.html` - Book details page (query param: `id`).
- `GET /upload.html` - Upload book page.
- `GET /bookshelf.html` - My Bookshelf page.
- `POST /upload` - Handle book upload (expects `bookFile`, `title`, `author`, `genre`, `keywords`).

### API Endpoints (Unprotected)

- `GET /api/books` - List all books (optional query params: `keyword`, `genre`, `author`).
  - If `author` and `genre` provided: both must match (AND).
  - If only one provided: that one must match.
  - If `keyword` provided: tokenized search, results scored and sorted by match count.
- `GET /api/book/<book_id>` - Get details for a specific book.
- `GET /api/bookshelf` - Get current user's bookshelf (requires session).
- `GET /api/bookshelf/check/<book_id>` - Check if a book is in current user's bookshelf.
- `POST /api/bookshelf/add` - Add a book to current user's bookshelf (expects `book_id`).
- `POST /api/bookshelf/remove` - Remove a book from current user's bookshelf (expects `book_id`).

## Search & Filter Behavior

### Keyword Search

- Tokenizes input on commas and whitespace.
- Matches tokens against book title, author, and keywords (case-insensitive, partial match).
- Each book scores 1 point per token matched.
- Results are sorted by descending score (most relevant first).

### Author & Genre Filters

- **Both provided**: Book must match both author AND genre.
- **Author only**: Book must match author.
- **Genre only**: Book must match genre.
- Partial, case-insensitive matching.

### Combined Search

- If author/genre AND keywords provided, filtered results are re-scored by keywords.

## Troubleshooting

### "Port 5000 already in use"

Another application is using port 5000. Either:
- Kill the process using port 5000, or
- Change the port in `server.py` (last line: `app.run(debug=True, port=5001)`).

### "No books available" on Browse

- Ensure books are uploaded via `/upload.html`.
- Check that `bookvals.txt` contains book entries (JSON lines).
- Verify the `books/` directory has PDF files.

### "Invalid username or password"

- Ensure you registered first on `/register.html`.
- Login credentials must match exactly (case-sensitive).
- Check `logininfo.txt` for stored credentials.

### PDF viewer not loading

- Ensure the uploaded PDF is in the `books/` folder.
- Check browser console for JavaScript errors (F12 → Console).
- PDF.js is loaded from CDN; ensure internet access.

### Session expires / redirected to login

- Sessions are stored in Flask memory (not persistent across server restarts).
- Log in again after restarting the server.

## Development Notes

- **Passwords**: Currently stored plaintext. For production, use `werkzeug.security.generate_password_hash()`.
- **Session**: Uses Flask's in-memory session (not persistent). Consider adding persistent session storage.
- **PDF Rendering**: Preview uses PDF.js from CDN. Full viewers use browser's native PDF handler.
- **Search**: Uses substring matching (case-insensitive). Can be made stricter (whole-word) if needed.

## Future Enhancements

- Persistent sessions (database).
- Password hashing and email verification.
- Download books (instead of reading in browser).
- Book reviews and ratings.
- Social sharing.
- Mobile-friendly responsive design improvements.
