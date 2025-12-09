from flask import Flask, request, send_from_directory, redirect, url_for, jsonify, session
import os
import json

from book_logic import uploader as UploaderClass, bookshelf as BookshelfClass

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'


def send_page(name):
    return send_from_directory(BASE_DIR, name)


@app.route('/')
def index():
    return send_page('home.html')


@app.route('/home.html')
def home_page():
    return send_page('home.html')


@app.route('/browse.html')
def browse_page():
    # serve the client-side browse page (static)
    return send_page('browse.html')


@app.route('/book.html')
def book_page():
    return send_page('book.html')


@app.route('/upload.html')
def upload_page():
    return send_page('upload.html')


@app.route('/login.html')
def login_page():
    return send_page('login.html')


@app.route('/register.html')
def register_page():
    return send_page('register.html')


@app.route('/bookshelf.html')
def bookshelf_page():
    return send_page('bookshelf.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route('/books/<path:filename>')
def books_files(filename):
    # Serve files from the books directory
    books_dir = os.path.join(BASE_DIR, 'books')
    return send_from_directory(books_dir, filename)


@app.route('/upload', methods=['POST'])
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
    # pass the FileStorage.stream and filename
    entry = uploader.upload_book(f.stream, f.filename, title, author, genre, keywords)

    # redirect to bookshelf page after successful upload
    return redirect(url_for('bookshelf_page'))


@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    # NOTE: this is a minimal placeholder; implement real auth as needed
    if not username or not password:
        return 'username and password required', 400
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
    shelf = BookshelfClass()
    shelf.instantiate()
    out = []
    for b in shelf.list_books():
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
