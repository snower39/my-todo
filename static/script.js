
// READ - 서버에서 할 일 목록 가져오기
async function loadTodos() {
    const response = await fetch("/api/todos");
    const todos = await response.json();

    const list = document.getElementById("todoList");
    list.innerHTML = "";

    todos.forEach(todo => {
        const li = document.createElement("li");

        const span = document.createElement("span");
        span.textContent = todo.title;
        span.style.marginRight = "10px";

        // 수정 버튼
        const editBtn = document.createElement("button");
        editBtn.textContent = "수정";
        editBtn.style.marginRight = "5px";

        editBtn.onclick = () => editTodo(todo.id, todo.title);

        // 삭제 버튼
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "삭제";
        deleteBtn.style.background = "#dc2626";

        deleteBtn.onclick = () => deleteTodo(todo.id);

        li.appendChild(span);
        li.appendChild(editBtn);
        li.appendChild(deleteBtn);

        list.appendChild(li);
    });
}

// CREATE - 새로운 할 일 추가
async function addTodo() {
    const input = document.getElementById("todoInput");
    const title = input.value.trim();

    if (title === "") {
        alert("할 일을 입력하세요!");
        return;
    }

    const response = await fetch("/api/todos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ title })
    });

    if (!response.ok) {
        alert("등록에 실패했습니다.");
        return;
    }

    input.value = "";
    await loadTodos();
}

// UPDATE - 할 일 수정
async function editTodo(id, oldTitle) {
    const title = prompt("할 일을 수정하세요", oldTitle);

    if (title === null) return;

    if (title.trim() === "") {
        alert("내용을 입력하세요.");
        return;
    }

    const response = await fetch(`/api/todos/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ title: title.trim() })
    });

    if (!response.ok) {
        alert("수정에 실패했습니다.");
        return;
    }

    await loadTodos();
}

// DELETE - 할 일 삭제
async function deleteTodo(id) {
    if (!confirm("정말 삭제하시겠습니까?")) {
        return;
    }

    const response = await fetch(`/api/todos/${id}`, {
        method: "DELETE"
    });

    if (!response.ok) {
        alert("삭제에 실패했습니다.");
        return;
    }

    await loadTodos();
}

// 페이지가 열리면 목록 조회
loadTodos();
