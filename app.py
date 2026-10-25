
import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-this-secret"
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "codesphere.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first to access this feature.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


CONTENT = {
    "learning": {
        "title": "Learning Hub",
        "intro": "Learn programming and IT skills at your own pace.",
        "items": [
            ("🐍", "Python Fundamentals", "Variables, loops, functions, and beginner exercises.", "https://docs.python.org/3/tutorial/"),
            ("🌐", "HTML and CSS", "Build responsive websites and modern layouts.", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
            ("⚡", "JavaScript", "Learn interactive web programming.", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
            ("🗄️", "Database Basics", "Learn about tables, queries, and relational databases.", "https://www.postgresql.org/docs/")
        ]
    },
    "projects": {
        "title": "Project Showcase",
        "intro": "Project ideas you can build and add to your portfolio.",
        "items": [
            ("🎓", "Student Management System", "Record students, subjects, and grades.", "https://github.com/topics/student-management-system"),
            ("🛒", "Inventory System", "Track products, stock, and transactions.", "https://github.com/topics/inventory-management"),
            ("🌦️", "Weather Dashboard", "Build a dashboard that uses a weather API.", "https://github.com/topics/weather-app"),
            ("🔐", "Login System", "Learn about authentication and password security.", "https://flask.palletsprojects.com/")
        ]
    },
    "tools": {
        "title": "Developer Tools",
        "intro": "Useful tools from their official websites.",
        "items": [
            ("💻", "Visual Studio Code", "A code editor for web development and Python.", "https://code.visualstudio.com/"),
            ("🐍", "Python", "A programming language for web development, automation, and data.", "https://www.python.org/downloads/"),
            ("🔧", "Git", "Version control for tracking code changes.", "https://git-scm.com/downloads"),
            ("🐙", "GitHub", "Host repositories and collaborate on projects.", "https://github.com/"),
            ("🧪", "Postman", "Test and debug APIs.", "https://www.postman.com/"),
            ("🗃️", "DB Browser for SQLite", "View and manage SQLite databases.", "https://sqlitebrowser.org/")
        ]
    },
    "careers": {
        "title": "IT Career Roadmap",
        "intro": "Choose a career path and identify the skills you need to learn.",
        "items": [
            ("🌐", "Web Developer", "HTML, CSS, JavaScript, Python, Flask, and databases.", "https://developer.mozilla.org/"),
            ("🛡️", "Cybersecurity Analyst", "Networking, Linux, security fundamentals, and ethical practices.", "https://www.cisa.gov/cybersecurity"),
            ("📊", "Data Analyst", "Excel, SQL, Python, statistics, and data visualization.", "https://pandas.pydata.org/docs/"),
            ("☁️", "Cloud Engineer", "Networking, Linux, cloud infrastructure, and deployment.", "https://aws.amazon.com/getting-started/"),
            ("🧑‍💻", "Software Engineer", "Programming, algorithms, testing, Git, and system design.", "https://github.com/resources/articles")
        ]
    },
    "community": {
        "title": "Tech Community",
        "intro": "Discussion prompts for IT students and professionals.",
        "items": [
            ("💬", "Introduce Yourself", "What are you studying, and what technology skill would you like to learn?", "https://github.com/orgs/community/discussions"),
            ("🧠", "Programming Tips", "Share coding tips and lessons you have learned.", "https://stackoverflow.com/questions"),
            ("🚀", "Project Feedback", "Showcase your project on GitHub and ask for feedback.", "https://github.com/explore"),
            ("🤝", "Collaboration", "Find open-source projects you can contribute to.", "https://goodfirstissue.dev/")
        ]
    },
    "about": {
        "title": "About CodeSphere",
        "intro": "Learn. Build. Connect. Innovate.",
        "items": [
            ("🎯", "Our Mission", "Make IT learning and career development more accessible."),
            ("🎓", "For Students", "Find learning resources, project ideas, and practice opportunities."),
            ("💼", "For Professionals", "Discover tools and continue developing your technical skills."),
            ("🌱", "Our Vision", "Build a supportive space for people who want to grow in technology.")
        ]
    }
}


@app.route("/")
def home():
    featured = [
        ("📚", "Learning Hub", "Learn programming and web development.", url_for("section", name="learning")),
        ("🧩", "Project Showcase", "Find project ideas for your portfolio.", url_for("section", name="projects")),
        ("🛠️", "Developer Tools", "Discover tools and official downloads.", url_for("section", name="tools")),
        ("🧭", "Career Roadmap", "Plan your next step in IT.", url_for("section", name="careers"))
    ]
    return render_template("page.html", page={
        "title": "Build Your Future in Tech",
        "intro": "Welcome to CodeSphere — your hub for learning, building projects, and growing your IT career.",
        "items": featured
    }, home=True)


@app.route("/<name>")
def section(name):
    if name not in CONTENT:
        return render_template("page.html", page={
            "title": "Page Not Found",
            "intro": "We couldn't find the page you were looking for.",
            "items": []
        }), 404
    return render_template("page.html", page=CONTENT[name], home=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "error")
        elif len(password) < 8:
            flash("The password must be at least 8 characters long.", "error")
        else:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password))
                )
                db.commit()
                session.clear()
                session["user_id"] = cursor.lastrowid
                session["username"] = username
                flash("Registration successful! Welcome to CodeSphere.", "success")
                return redirect(url_for("home"))
            except sqlite3.IntegrityError:
                flash("An account with that email address already exists.", "error")

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("You have successfully logged in.", "success")
            return redirect(url_for("home"))

        flash("Incorrect email address or password.", "error")

    return render_template("auth.html", mode="login")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    return render_template("page.html", page={
        "title": "My Profile",
        "intro": f"Welcome, {session.get('username')}! You are logged in to CodeSphere.",
        "items": [
            ("👤", "Account", "You now have your own CodeSphere account."),
            ("📚", "Learning", "Visit the Learning Hub to begin your learning journey."),
            ("🚀", "Next Step", "Build your first project and add it to your portfolio.")
        ]
    }, home=False)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in all fields.", "error")
        elif len(message) > 5000:
            flash("Your message is too long (maximum 5000 characters).", "error")
        else:
            get_db().execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message)
            )
            get_db().commit()
            flash("Thank you! Your feedback has been saved.", "success")
            return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
