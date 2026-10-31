
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 임시로 할 일을 저장할 리스트
todos = []

# 웹페이지 표시
@app.route("/")
def home():
    return render_template("index.html")

# 할 일 목록 조회 (GET)
@app.route("/api/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

# 새로운 할 일 등록 (POST)
@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "할 일을 입력하세요"}), 400

    todo = {
        "id": len(todos) + 1,
        "title": title.strip()
    }

    todos.append(todo)
    return jsonify(todo), 201

if __name__ == "__main__":
    app.run(debug=True)
