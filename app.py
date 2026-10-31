
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
import sqlite3
import os
import secrets

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "todos.db"
SECRET_FILE = BASE_DIR / ".flask_secret"

# 로컬 개발용 세션 암호화 키
if os.environ.get("FLASK_SECRET_KEY"):
    app.secret_key = os.environ["FLASK_SECRET_KEY"]
else:
    if not SECRET_FILE.exists():
        SECRET_FILE.write_text(
            secrets.token_hex(32), encoding="utf-8"
        )
    app.secret_key = SECRET_FILE.read_text(
        encoding="utf-8"
    ).strip()

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# DB 초기화 및 기존 데이터 보존
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT '보통',
            user_id INTEGER REFERENCES users(id)
        )
    """)

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(todos)")
    ]

    if "completed" not in columns:
        conn.execute("""
            ALTER TABLE todos
            ADD COLUMN completed INTEGER NOT NULL DEFAULT 0
        """)

    if "priority" not in columns:
        conn.execute("""
            ALTER TABLE todos
            ADD COLUMN priority TEXT NOT NULL DEFAULT '보통'
        """)

    if "user_id" not in columns:
        conn.execute("""
            ALTER TABLE todos
            ADD COLUMN user_id INTEGER REFERENCES users(id)
        """)

    conn.commit()
    conn.close()

# 로그인 필요 여부 확인
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "로그인이 필요합니다"
                }), 401
            return redirect(url_for("login"))

        return view(*args, **kwargs)
    return wrapped

# 회원가입
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_confirm = request.form.get(
        "password_confirm", ""
    )

    if not (3 <= len(username) <= 30):
        return render_template(
            "register.html",
            error="아이디는 3~30자로 입력하세요."
        )

    if len(password) < 8:
        return render_template(
            "register.html",
            error="비밀번호는 8자 이상이어야 합니다."
        )

    if password != password_confirm:
        return render_template(
            "register.html",
            error="비밀번호가 일치하지 않습니다."
        )

    password_hash = generate_password_hash(password)

    conn = get_db()

    try:
        cursor = conn.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))

        new_user_id = cursor.lastrowid

        # 기존 할 일은 최초 가입 계정에 연결
        # 이미 다른 사용자가 있으면 자동 이전하지 않음
        user_count = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        if user_count == 1:
            conn.execute("""
                UPDATE todos
                SET user_id = ?
                WHERE user_id IS NULL
            """, (new_user_id,))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.rollback()
        return render_template(
            "register.html",
            error="이미 사용 중인 아이디입니다."
        )

    finally:
        conn.close()

    return redirect(url_for("login"))

# 로그인
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = get_db()

    user = conn.execute("""
        SELECT id, username, password_hash
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()

    conn.close()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return render_template(
            "login.html",
            error="아이디 또는 비밀번호가 올바르지 않습니다."
        )

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return redirect(url_for("home"))

# 로그아웃
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# 메인 화면
@app.route("/")
@login_required
def home():
    return render_template(
        "index.html",
        username=session["username"]
    )

# READ - 본인의 할 일 조회
@app.route("/api/todos", methods=["GET"])
@login_required
def get_todos():
    conn = get_db()

    rows = conn.execute("""
        SELECT id, title, completed, priority
        FROM todos
        WHERE user_id = ?
        ORDER BY id DESC
    """, (session["user_id"],)).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

# CREATE - 본인의 할 일 등록
@app.route("/api/todos", methods=["POST"])
@login_required
def add_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")
    priority = data.get("priority", "보통")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "할 일을 입력하세요"}), 400

    if priority not in ["높음", "보통", "낮음"]:
        return jsonify({"error": "우선순위 오류"}), 400

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO todos (title, completed, priority, user_id)
        VALUES (?, 0, ?, ?)
    """, (
        title.strip(),
        priority,
        session["user_id"]
    ))

    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": todo_id,
        "title": title.strip(),
        "completed": 0,
        "priority": priority
    }), 201

# UPDATE - 본인의 할 일 제목 수정
@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
@login_required
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "내용을 입력하세요"}), 400

    conn = get_db()

    cursor = conn.execute("""
        UPDATE todos
        SET title = ?
        WHERE id = ? AND user_id = ?
    """, (
        title.strip(),
        todo_id,
        session["user_id"]
    ))

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "수정 완료"})

# UPDATE - 본인의 할 일 완료 상태 변경
@app.route("/api/todos/<int:todo_id>/complete", methods=["PUT"])
@login_required
def complete_todo(todo_id):
    data = request.get_json(silent=True) or {}
    completed = data.get("completed")

    if type(completed) is not bool:
        return jsonify({"error": "완료 상태 오류"}), 400

    conn = get_db()

    cursor = conn.execute("""
        UPDATE todos
        SET completed = ?
        WHERE id = ? AND user_id = ?
    """, (
        int(completed),
        todo_id,
        session["user_id"]
    ))

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "완료 상태 변경"})

# UPDATE - 본인의 할 일 우선순위 변경
@app.route("/api/todos/<int:todo_id>/priority", methods=["PUT"])
@login_required
def priority_todo(todo_id):
    data = request.get_json(silent=True) or {}
    priority = data.get("priority")

    if priority not in ["높음", "보통", "낮음"]:
        return jsonify({"error": "우선순위 오류"}), 400

    conn = get_db()

    cursor = conn.execute("""
        UPDATE todos
        SET priority = ?
        WHERE id = ? AND user_id = ?
    """, (
        priority,
        todo_id,
        session["user_id"]
    ))

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "우선순위 변경"})

# DELETE - 본인의 할 일 삭제
@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
@login_required
def delete_todo(todo_id):
    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM todos
        WHERE id = ? AND user_id = ?
    """, (
        todo_id,
        session["user_id"]
    ))

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "삭제 완료"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
