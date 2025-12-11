from flask import Flask, request, send_from_directory, redirect, url_for, jsonify, session
from functools import wraps
import os
import json
import re

from book_logic import uploader as UploaderClass, bookshelf as BookshelfClass

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'


def login_required(f):
    """Decorator to require login. Redirects to login.html if not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def send_page(name):
    return send_from_directory(BASE_DIR, name)


@app.route('/')
def index():
    return send_page('home.html')


@app.route('/home.html')
@login_required
def home_page():
    return send_page('home.html')


@app.route('/browse.html')
@login_required
def browse_page():
    # serve the client-side browse page (static)
    return send_page('browse.html')


@app.route('/book.html')
@login_required
def book_page():
    return send_page('book.html')


@app.route('/upload.html')
@login_required
def upload_page():
    return send_page('upload.html')


@app.route('/login.html')
def login_page():
    return send_page('login.html')


@app.route('/register.html')
def register_page():
    return send_page('register.html')


@app.route('/bookshelf.html')
@login_required
def bookshelf_page():
    return send_page('bookshelf.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route('/styles.css')
def styles():
    return send_from_directory(BASE_DIR, 'styles.css')


@app.route('/app.js')
def appjs():
    return send_from_directory(BASE_DIR, 'app.js')


@app.route('/books/<path:filename>')
def books_files(filename):
    # Serve files from the books directory
    books_dir = os.path.join(BASE_DIR, 'books')
    return send_from_directory(books_dir, filename)


@app.route('/upload', methods=['POST'])
@login_required
def handle_upload():
    # simple upload handler that uses book_logic.uploader
    f = request.files.get('bookFile')
    if not f:
        return 'No file provided', 400

    title = request.form.get('title', '')
    author = request.form.get('author', '')
    genre = request.form.get('genre', '')
    keywords = request.form.get('keywords', '')

    username = session.get('username') or request.form.get('username') or 'anonymous'

    uploader = UploaderClass(username, '', '')
    # read file bytes from the FileStorage to avoid stream access issues
    file_bytes = f.read()
    entry = uploader.upload_book(file_bytes, f.filename, title, author, genre, keywords)

    # redirect to bookshelf page after successful upload
    return redirect(url_for('bookshelf_page'))


@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return 'username and password required', 400

    # Load credentials from logininfo.txt
    login_path = os.path.join(BASE_DIR, 'logininfo.txt')
    users = {}
    if os.path.exists(login_path):
        try:
            with open(login_path, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except Exception:
            users = {}

    # Check if username exists and password matches
    if username not in users or users[username].get('password') != password:
        return 'Invalid username or password', 401

    session['username'] = username
    return redirect(url_for('home_page'))


@app.route('/register', methods=['POST'])
def handle_register():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return 'username and password required', 400

    users_path = os.path.join(BASE_DIR, 'users.json')
    users = {}
    if os.path.exists(users_path):
        try:
            with open(users_path, 'r', encoding='utf-8') as uf:
                users = json.load(uf)
        except Exception:
            users = {}

    if username in users:
        return 'user exists', 400

    users[username] = {'password': password}
    with open(users_path, 'w', encoding='utf-8') as uf:
        json.dump(users, uf)

    session['username'] = username
    return redirect(url_for('home_page'))


@app.route('/api/books', methods=['GET'])
def api_books():
    # Support optional search parameters. If none provided, return all books.
    # `keyword` may contain one or more tokens (comma or space separated).
    keyword_raw = request.args.get('keyword', '') or request.args.get('keywords', '')
    keyword_raw = keyword_raw.strip().lower()
    genre_q = request.args.get('genre', '').strip().lower()
    author_q = request.args.get('author', '').strip().lower()

    # tokenize keywords into distinct tokens
    kw_tokens = []
    if keyword_raw:
        # split on commas or whitespace
        kw_tokens = [t for t in re.split('[,\s]+', keyword_raw) if t]

    shelf = BookshelfClass()
    shelf.instantiate()
    books = shelf.list_books()

    results = []

    # If author_q or genre_q provided, filter by them.
    # - If both provided: both must match (AND)
    # - If only one provided: only that one must match
    if author_q or genre_q:
        for b in books:
            try:
                author_match = True
                genre_match = True
                if author_q:
                    author_match = author_q in (b.author or '').lower()
                if genre_q:
                    genre_match = genre_q in (b.genre or '').lower()
                # if both provided, require both; if only one provided, require that one
                match = True
                if author_q and genre_q:
                    match = author_match and genre_match
                else:
                    match = (author_q and author_match) or (genre_q and genre_match)
            except Exception:
                match = False
            if match:
                results.append((b, 0))
        # If keywords provided, compute keyword scores for the filtered results and sort
        if kw_tokens:
            scored = []
            for b, _ in results:
                try:
                    cnt = 0
                    title_l = (b.title or '').lower()
                    author_l = (b.author or '').lower()
                    kws = [str(x).lower() for x in (b.keywords or [])]
                    for tok in kw_tokens:
                        if tok in title_l or tok in author_l:
                            cnt += 1
                            continue
                        for kw in kws:
                            if tok in kw:
                                cnt += 1
                                break
                    scored.append((b, cnt))
                except Exception:
                    scored.append((b, 0))
            # sort by count descending
            scored.sort(key=lambda it: it[1], reverse=True)
            results = scored
    elif kw_tokens:
        # Keyword scoring: count how many distinct tokens match title/author/keywords
        for b in books:
            try:
                cnt = 0
                title_l = (b.title or '').lower()
                author_l = (b.author or '').lower()
                kws = [str(x).lower() for x in (b.keywords or [])]
                for tok in kw_tokens:
                    if tok in title_l or tok in author_l:
                        cnt += 1
                        continue
                    for kw in kws:
                        if tok in kw:
                            cnt += 1
                            break
                if cnt > 0:
                    results.append((b, cnt))
            except Exception:
                continue
        # sort by count descending
        results.sort(key=lambda it: it[1], reverse=True)
    else:
        # no filters: include all
        for b in books:
            results.append((b, 0))

    out = []
    for b, score in results:
        out.append({
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'genre': b.genre,
            'keywords': b.keywords,
            'file_path': b.file_path,
            'uploader': b.uploader,
            'timestamp': b.timestamp,
            'score': score,
        })
    return jsonify(out)


@app.route('/api/book/<book_id>', methods=['GET'])
def api_book(book_id):
    shelf = BookshelfClass()
    shelf.instantiate()
    for b in shelf.list_books():
        if str(b.id) == str(book_id):
            return jsonify({
                'id': b.id,
                'title': b.title,
                'author': b.author,
                'genre': b.genre,
                'keywords': b.keywords,
                'file_path': b.file_path,
                'uploader': b.uploader,
                'timestamp': b.timestamp,
            })
    return jsonify({'error': 'not found'}), 404


def _get_username():
    return session.get('username') or 'anonymous'


def _load_shelves():
    path = os.path.join(BASE_DIR, 'usershelves.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_shelves(data):
    path = os.path.join(BASE_DIR, 'usershelves.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


@app.route('/api/bookshelf/check/<book_id>', methods=['GET'])
def api_bookshelf_check(book_id):
    username = _get_username()
    shelves = _load_shelves()
    user_list = shelves.get(username, [])
    return jsonify({'in_shelf': str(book_id) in [str(x) for x in user_list]})


@app.route('/api/bookshelf/add', methods=['POST'])
def api_bookshelf_add():
    book_id = request.form.get('book_id') or (request.json and request.json.get('book_id'))
    if not book_id:
        return jsonify({'error': 'missing book_id'}), 400
    username = _get_username()
    shelves = _load_shelves()
    user_list = shelves.get(username, [])
    if book_id not in [str(x) for x in user_list]:
        user_list.append(book_id)
    shelves[username] = user_list
    _save_shelves(shelves)
    return jsonify({'ok': True})


@app.route('/api/bookshelf/remove', methods=['POST'])
def api_bookshelf_remove():
    book_id = request.form.get('book_id') or (request.json and request.json.get('book_id'))
    if not book_id:
        return jsonify({'error': 'missing book_id'}), 400
    username = _get_username()
    shelves = _load_shelves()
    user_list = shelves.get(username, [])
    user_list = [x for x in user_list if str(x) != str(book_id)]
    shelves[username] = user_list
    _save_shelves(shelves)
    return jsonify({'ok': True})


@app.route('/api/bookshelf', methods=['GET'])
def api_bookshelf_list():
    username = _get_username()
    shelves = _load_shelves()
    book_ids = shelves.get(username, [])
    # return full metadata for each book id
    shelf = BookshelfClass()
    shelf.instantiate()
    mapping = {str(b.id): b for b in shelf.list_books()}
    out = []
    for bid in book_ids:
        b = mapping.get(str(bid))
        if b:
            out.append({
                'id': b.id,
                'title': b.title,
                'author': b.author,
                'genre': b.genre,
                'keywords': b.keywords,
                'file_path': b.file_path,
                'uploader': b.uploader,
                'timestamp': b.timestamp,
            })
    return jsonify(out)


if __name__ == '__main__':
    app.run(debug=True)
