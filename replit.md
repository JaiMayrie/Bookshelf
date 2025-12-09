# Book Organizer

A static HTML website for organizing and managing books.

## Overview
- **Purpose**: Book collection management app
- **Type**: Static HTML website with client-side JavaScript
- **State**: Uses browser localStorage for data persistence

## Project Structure
- `home.html` - Main landing page
- `browse.html` - Browse/search books
- `bookshelf.html` - Personal bookshelf view
- `upload.html` - Add new books
- `login.html` / `register.html` - User authentication UI
- `styles.css` - Global styles
- `app.js` - Client-side JavaScript logic
- `server.py` - Simple Python HTTP server for local development

## Running the Project
The project uses a Python static file server on port 5000:
```
python server.py
```

## Features
- Browse book library
- Add new books
- Manage personal bookshelf
- Search books by title, author, or genre
- Simple login/register (localStorage only)
