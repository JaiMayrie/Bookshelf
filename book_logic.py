import os
import json
import datetime
import shutil
import uuid

class user:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class reader(user):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.borrowed_books = []
        self.bookmarked_books = []
        self.currentbook = None
    def add_to_reading_list(self, book):
        self.borrowed_books.append(book)
    def choose_book(self, book):
        self.currentbook = book
    def bookmark_book(self, book):
        self.bookmarked_books.append(book)
    def open_book(self):
        return self.currentbook

class uploader(user):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
        self.uploaded_books = []
    def upload_book(self, file, filename, title, author, genre, keywords):
        base_dir = os.path.dirname(__file__)
        books_dir = os.path.join(base_dir, 'books')
        os.makedirs(books_dir, exist_ok=True)

        # sanitize incoming filename
        save_name = os.path.basename(filename)
        dest_path = os.path.join(books_dir, save_name)

        # avoid filename collisions by appending a counter
        name, ext = os.path.splitext(save_name)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(books_dir, f"{name}_{counter}{ext}")
            counter += 1

        # Write file depending on provided type
        if isinstance(file, (bytes, bytearray)):
            with open(dest_path, 'wb') as out_f:
                out_f.write(file)
        elif hasattr(file, 'read'):
            content = file.read()
            if isinstance(content, str):
                content = content.encode('utf-8')
            with open(dest_path, 'wb') as out_f:
                out_f.write(content)
        elif isinstance(file, str) and os.path.exists(file):
            shutil.copyfile(file, dest_path)
        else:
            raise ValueError('Unsupported file type for upload')

        # normalize keywords into a list
        if isinstance(keywords, str):
            kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
        elif isinstance(keywords, (list, tuple)):
            kw_list = [str(k) for k in keywords]
        else:
            kw_list = []

        entry = {
            'id': str(uuid.uuid4()),
            'filename': os.path.basename(dest_path),
            'file_path': os.path.join('books', os.path.basename(dest_path)),
            'title': title,
            'author': author,
            'genre': genre,
            'keywords': kw_list,
            'uploader': self.username,
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }

        vals_path = os.path.join(base_dir, 'bookvals.txt')
        # append as a single JSON line
        with open(vals_path, 'a', encoding='utf-8') as vf:
            vf.write(json.dumps(entry, ensure_ascii=False) + '\n')

        # update uploader state
        self.uploaded_books.append(entry)
        return entry
        
class bookshelf:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        self.books.append(book)

    def list_books(self):
        return self.books
    def search_books(bookshelf, keyword):
        return [book for book in bookshelf.list_books() if book.matches_keyword(keyword)]
    def instantiate(self, vals_path=None):
        base_dir = os.path.dirname(__file__)
        if vals_path is None:
            vals_path = os.path.join(base_dir, 'bookvals.txt')

        inst = []
        if not os.path.exists(vals_path):
            self.books = []
            return inst

        with open(vals_path, 'r', encoding='utf-8') as vf:
            for line in vf:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    # skip malformed lines
                    continue

                # ensure id exists
                if 'id' not in entry or not entry.get('id'):
                    entry['id'] = str(uuid.uuid4())

                # normalize keywords
                kws = entry.get('keywords', [])
                if isinstance(kws, str):
                    kws = [k.strip() for k in kws.split(',') if k.strip()]

                # determine file_path
                file_path = entry.get('file_path')
                if not file_path:
                    fname = entry.get('filename')
                    if fname:
                        file_path = os.path.join('books', fname)

                b = book(
                    title=entry.get('title'),
                    author=entry.get('author'),
                    genre=entry.get('genre'),
                    keywords=kws,
                    file_path=file_path,
                    id=entry.get('id'),
                    uploader=entry.get('uploader'),
                    timestamp=entry.get('timestamp')
                )
                inst.append(b)

        # replace shelf contents
        self.books = inst
        return self.books
class book:
    def __init__(self, title, author, genre, keywords, file_path=None, id=None, uploader=None, timestamp=None):
        self.id = id
        self.title = title
        self.author = author
        self.genre = genre
        self.keywords = keywords if keywords is not None else []
        self.file_path = file_path
        self.uploader = uploader
        self.timestamp = timestamp
    def __repr__(self):
        return f"Book(id={self.id}, title={self.title}, author={self.author}, genre={self.genre}, keywords={self.keywords})"
    def matches_keyword(self, keyword):
        try:
            return keyword in self.keywords
        except Exception:
            return False
