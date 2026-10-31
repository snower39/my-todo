
from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

# 데이터베이스 파일 위치
DB_PATH = Path(__file__).resolve().parent / "todos.db"

# 데이터베이스 연결
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 테이블 생성
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# 메인 웹페이지
@app.route("/")
def home():
    return render_template("index.html")

# 할 일 목록 조회 (SELECT)
@app.route("/api/todos", methods=["GET"])
def get_todos():
    conn = get_db()

    rows = conn.execute(
        "SELECT id, title FROM todos ORDER BY id DESC"
    ).fetchall()

    conn.close()

    todos = [dict(row) for row in rows]
    return jsonify(todos)

# 새로운 할 일 등록 (INSERT)
@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "할 일을 입력하세요"}), 400

    conn = get_db()

    cursor = conn.execute(
        "INSERT INTO todos (title) VALUES (?)",
        (title.strip(),)
    )

    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": todo_id,
        "title": title.strip()
    }), 201

# 데이터베이스 초기화
init_db()

if __name__ == "__main__":
    app.run(debug=True)
