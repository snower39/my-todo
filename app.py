
from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).resolve().parent / "todos.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 생성 및 기존 테이블 확장
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            priority TEXT NOT NULL DEFAULT '보통'
        )
    """)

    # 기존 3~4주차 DB에도 컬럼 추가
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

    conn.commit()
    conn.close()

# 메인 화면
@app.route("/")
def home():
    return render_template("index.html")

# READ - 목록 조회
@app.route("/api/todos", methods=["GET"])
def get_todos():
    conn = get_db()

    rows = conn.execute("""
        SELECT id, title, completed, priority
        FROM todos
        ORDER BY id DESC
    """).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

# CREATE - 할 일 등록
@app.route("/api/todos", methods=["POST"])
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
        INSERT INTO todos (title, completed, priority)
        VALUES (?, 0, ?)
    """, (title.strip(), priority))

    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": todo_id,
        "title": title.strip(),
        "completed": 0,
        "priority": priority
    }), 201

# UPDATE - 제목 수정
@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "내용을 입력하세요"}), 400

    conn = get_db()

    cursor = conn.execute(
        "UPDATE todos SET title = ? WHERE id = ?",
        (title.strip(), todo_id)
    )

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "수정 완료"})

# UPDATE - 완료 상태 변경
@app.route("/api/todos/<int:todo_id>/complete", methods=["PUT"])
def complete_todo(todo_id):
    data = request.get_json(silent=True) or {}
    completed = data.get("completed")

    if type(completed) is not bool:
        return jsonify({"error": "완료 상태 오류"}), 400

    conn = get_db()

    cursor = conn.execute(
        "UPDATE todos SET completed = ? WHERE id = ?",
        (int(completed), todo_id)
    )

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "완료 상태 변경"})

# UPDATE - 우선순위 변경
@app.route("/api/todos/<int:todo_id>/priority", methods=["PUT"])
def priority_todo(todo_id):
    data = request.get_json(silent=True) or {}
    priority = data.get("priority")

    if priority not in ["높음", "보통", "낮음"]:
        return jsonify({"error": "우선순위 오류"}), 400

    conn = get_db()

    cursor = conn.execute(
        "UPDATE todos SET priority = ? WHERE id = ?",
        (priority, todo_id)
    )

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "우선순위 변경"})

# DELETE - 할 일 삭제
@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM todos WHERE id = ?",
        (todo_id,)
    )

    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "할 일이 없습니다"}), 404

    return jsonify({"message": "삭제 완료"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
