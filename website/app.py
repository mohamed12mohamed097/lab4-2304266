import os
import re
import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
import uuid
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def home():
    return "Flask is working"





@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors={}, form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    # same rules as the JavaScript
    errors = {}
    if name == "":
        errors["name"] = "Name is required"
    if email == "":
        errors["email"] = "Email is required"
    if password == "":
        errors["password"] = "Password is required"
    if confirm == "":
        errors["confirm_password"] = "Confirm password is required"
    elif password != "" and password != confirm:
        errors["confirm_password"] = "Passwords do not match"

    if errors:
        return render_template("register.html", errors=errors, form=request.form)

    # hash the password (never store the password itself)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                (email, name, password_hash),
            )
            new_id = cur.lastrowid
        conn.commit()
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if e.args[0] == 1062:  # duplicate email (UNIQUE)
            errors["email"] = "Email Already Exists"
            return render_template("register.html", errors=errors, form=request.form)
        raise
    finally:
        conn.close()

    # log the user in, then redirect so refresh does not resend the form
    session["user_id"] = new_id
    session["name"] = name
    return redirect("/todos")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", errors={}, form={})

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = {}
    if email == "":
        errors["email"] = "Email is required"
    if password == "":
        errors["password"] = "Password is required"

    if errors:
        return render_template("login.html", errors=errors, form=request.form)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    # same message for unknown email and wrong password
    if user is None or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        errors["login"] = "Invalid email or password"
        return render_template("login.html", errors=errors, form=request.form)

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def render_todos(error=None, form_title="", error_id=None):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC",
                (session["user_id"],),
            )
            items = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        "todos.html",
        items=items,
        name=session["name"],
        error=error,
        form_title=form_title,
        error_id=error_id,
    )


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")
    return render_todos()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title", "").strip()

    error = None
    if title == "":
        error = "Title is required"
    elif len(title) > 200:
        error = "Title is too long (200 characters at most)"

    if error:
        return render_todos(error=error, form_title=request.form.get("title", ""))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                (session["user_id"], title),
            )
        conn.commit()
    finally:
        conn.close()

    return redirect("/todos")

def validate_title(raw):
    title = raw.strip()
    if title == "":
        return title, "Title is required"
    if len(title) > 200:
        return title, "Title is too long (200 characters at most)"
    return title, None


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    title, error = validate_title(request.form.get("title", ""))
    if error:
        return render_todos(error=error, error_id=todo_id)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
                (title, todo_id, session["user_id"]),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/done", methods=["POST"])
def done_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    is_done = 1 if request.form.get("is_done") == "1" else 0

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                (is_done, todo_id, session["user_id"]),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect("/todos")


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, session["user_id"]),
            )
        conn.commit()
    finally:
        conn.close()
    return redirect("/todos")

# ---------------- LIBRARY (Lab 3 + Lab 4) ----------------
UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# the report pages read their SQL from problem2_Queries.sql
QUERY_FILE = os.path.join(app.root_path, "..", "problem2_Queries.sql")
REPORT_PAGES = {
    "F2.2": "Catalogue",
    "F2.3": "Reports",
    "F2.4": "Loans",
    "F2.5": "Most borrowed",
    "F2.6": "Authors and books",
}


@app.errorhandler(413)
def too_large(e):
    return redirect("/library?error=Image is too large (5 MB at most)")


def save_image(file):
    """Save an uploaded image. Return (filename or None, error or None)."""
    if file is None or file.filename == "":
        return None, None
    ext = secure_filename(file.filename).rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        return None, "Image must be png, jpg, jpeg, gif or webp"
    filename = uuid.uuid4().hex + "." + ext
    file.save(os.path.join(UPLOAD_DIR, filename))
    return filename, None


def get_library_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="library",
        cursorclass=pymysql.cursors.DictCursor,
    )


def query_library(sql, params=None):
    """Run one SELECT. The values go in params (placeholders), never inside the SQL text."""
    conn = get_library_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def run_library(sql, params):
    """Run one INSERT/UPDATE/DELETE. Return an error message, or None if it worked."""
    conn = get_library_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
        return None
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if e.args[0] == 1452:
            return "The author, publisher or category does not exist"
        return "Database error: " + str(e.args[1])
    finally:
        conn.close()

def delete_image_files(names):
    """Remove uploaded image files from static/uploads (ignores empty names)."""
    for name in names:
        if name:
            path = os.path.join(UPLOAD_DIR, name)
            if os.path.isfile(path):
                os.remove(path)

def lists_for_forms():
    return dict(
        authors=query_library("SELECT author_id, name FROM author ORDER BY name"),
        publishers=query_library("SELECT publisher_id, name FROM publisher ORDER BY name"),
        categories=query_library("SELECT category_id, name FROM category ORDER BY name"),
    )


def check_book(form):
    title = form.get("title", "").strip()
    price = form.get("price", "").strip()
    year = form.get("publish_year", "").strip()
    author_id = form.get("author_id", "").strip()
    publisher_id = form.get("publisher_id", "").strip()
    category_id = form.get("category_id", "").strip()
    if title == "":
        return None, "Title is required"
    if len(title) > 100:
        return None, "Title is too long (100 characters at most)"
    try:
        price_value = round(float(price), 2)
        if price_value < 0:
            raise ValueError
    except ValueError:
        return None, "Price must be a positive number"
    if year != "" and not year.isdigit():
        return None, "Year must be a number"
    if not author_id.isdigit():
        return None, "Choose an author"
    if not publisher_id.isdigit():
        return None, "Choose a publisher"
    if not category_id.isdigit():
        return None, "Choose a category"
    return (title, price_value, int(year) if year else None,
            int(author_id), int(publisher_id), int(category_id)), None


def check_author(form):
    name = form.get("name", "").strip()
    country = form.get("country", "").strip()
    if name == "":
        return None, "Name is required"
    if len(name) > 50 or len(country) > 50:
        return None, "Name and country are 50 characters at most"
    return (name, country), None


@app.route("/library")
def library():
    books = query_library(
        "SELECT book_id, title, price, publish_year, author_id, publisher_id, "
        "category_id, image FROM book ORDER BY book_id")
    authors = query_library(
        "SELECT author_id, name, country, image FROM author ORDER BY author_id")
    lists = lists_for_forms()
    lists.pop("authors")  # the full authors list above is used for the dropdown too
    return render_template(
        "library.html", books=books, authors=authors,
        error=request.args.get("error"), **lists)

@app.route("/library/book/add", methods=["POST"])
def add_book():
    data, error = check_book(request.form)
    image = None
    if not error:
        image, error = save_image(request.files.get("image"))
    if not error:
        error = run_library(
            "INSERT INTO book (title, price, publish_year, author_id, publisher_id, "
            "category_id, image) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            data + (image,),
        )
    return redirect("/library" + ("?error=" + error if error else ""))


@app.route("/library/author/add", methods=["POST"])
def add_author():
    data, error = check_author(request.form)
    image = None
    if not error:
        image, error = save_image(request.files.get("image"))
    if not error:
        error = run_library(
            "INSERT INTO author (name, country, image) VALUES (%s, %s, %s)",
            data + (image,),
        )
    return redirect("/library" + ("?error=" + error if error else ""))


@app.route("/library/book/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    error = None
    if request.method == "POST":
        data, error = check_book(request.form)
        image = None
        if not error:
            image, error = save_image(request.files.get("image"))
        if not error:
            sql = ("UPDATE book SET title = %s, price = %s, publish_year = %s, "
                   "author_id = %s, publisher_id = %s, category_id = %s")
            if image:
                error = run_library(sql + ", image = %s WHERE book_id = %s",
                                    data + (image, book_id))
            else:
                error = run_library(sql + " WHERE book_id = %s", data + (book_id,))
            if not error:
                return redirect("/library")
    rows = query_library("SELECT * FROM book WHERE book_id = %s", (book_id,))
    if not rows:
        return redirect("/library")
    return render_template("library_edit.html", kind="book", row=rows[0],
                           error=error, **lists_for_forms())


@app.route("/library/author/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    error = None
    if request.method == "POST":
        data, error = check_author(request.form)
        image = None
        if not error:
            image, error = save_image(request.files.get("image"))
        if not error:
            if image:
                error = run_library(
                    "UPDATE author SET name = %s, country = %s, image = %s WHERE author_id = %s",
                    data + (image, author_id),
                )
            else:
                error = run_library(
                    "UPDATE author SET name = %s, country = %s WHERE author_id = %s",
                    data + (author_id,),
                )
            if not error:
                return redirect("/library")
    rows = query_library("SELECT * FROM author WHERE author_id = %s", (author_id,))
    if not rows:
        return redirect("/library")
    return render_template("library_edit.html", kind="author", row=rows[0],
                           error=error, **lists_for_forms())


@app.route("/library/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    rows = query_library("SELECT image FROM book WHERE book_id = %s", (book_id,))
    error = run_library("DELETE FROM book WHERE book_id = %s", (book_id,))
    if not error:
        delete_image_files([r["image"] for r in rows])
    return redirect("/library" + ("?error=" + error if error else ""))


@app.route("/library/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    # the author's photo AND the covers of all his or her books (they are deleted too)
    photos = query_library("SELECT image FROM author WHERE author_id = %s", (author_id,))
    covers = query_library("SELECT image FROM book WHERE author_id = %s", (author_id,))
    error = run_library("DELETE FROM author WHERE author_id = %s", (author_id,))
    if not error:
        delete_image_files([r["image"] for r in photos + covers])
    return redirect("/library" + ("?error=" + error if error else ""))


# ---------------- Lab 4 pages ----------------
@app.route("/library/search")
def library_search():
    """F2.1 + BONUS: the typed values go in as %s placeholders (prepared statement)."""
    form = {k: request.args.get(k, "").strip()
            for k in ("title", "min_price", "max_price", "category")}
    categories = query_library("SELECT category_id, name FROM category ORDER BY name")
    books, error = None, None

    if request.args:  # the form was submitted
        try:
            low = float(form["min_price"]) if form["min_price"] else 0
            high = float(form["max_price"]) if form["max_price"] else 999999
        except ValueError:
            error = "Prices must be numbers"
        if error is None:
            sql = ("SELECT b.book_id, b.title, b.price, b.publish_year, c.name AS category "
                   "FROM book b JOIN category c ON b.category_id = c.category_id "
                   "WHERE b.title LIKE %s AND b.price BETWEEN %s AND %s")
            params = ["%" + form["title"] + "%", low, high]
            if form["category"].isdigit():
                sql += " AND b.category_id = %s"
                params.append(int(form["category"]))
            sql += " ORDER BY b.price ASC"
            books = query_library(sql, params)

    return render_template("library_search.html", form=form, categories=categories,
                           books=books, error=error)


def load_queries():
    """Split problem2_Queries.sql by the '-- F2.x (a) title' comments."""
    sections, current = {}, None
    with open(QUERY_FILE, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"--\s*(F2\.\d)\s*(?:\(([a-c])\))?\s*(.*)", line)
            if m:
                prefix = "(" + m.group(2) + ") " if m.group(2) else ""
                current = {"title": prefix + m.group(3).strip(), "sql": ""}
                sections.setdefault(m.group(1), []).append(current)
            elif current is not None and not line.strip().startswith("--"):
                current["sql"] += line
    return sections


@app.route("/library/page/<code>")
def library_page(code):
    if code not in REPORT_PAGES:
        return redirect("/library")
    sections = []
    for q in load_queries().get(code, []):
        rows = query_library(q["sql"].strip().rstrip(";"))
        sections.append({"title": q["title"], "rows": rows,
                         "columns": list(rows[0].keys()) if rows else []})
    return render_template("library_report.html", code=code,
                           name=REPORT_PAGES[code], sections=sections)
# ---------------- END LIBRARY ----------------

if __name__ == "__main__":
    app.run(debug=False)