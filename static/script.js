
// READ - 할 일 목록 조회
async function loadTodos() {
    const response = await fetch("/api/todos");
    const todos = await response.json();

    const list = document.getElementById("todoList");
    list.innerHTML = "";

    todos.forEach(todo => {
        const li = document.createElement("li");
        li.className = "todo-item";

        // 완료 체크박스
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = todo.completed === 1;

        checkbox.onchange = () => {
            changeCompleted(todo.id, checkbox.checked);
        };

        // 할 일 제목
        const span = document.createElement("span");
        span.textContent = todo.title;
        span.className = "todo-title";

        if (todo.completed === 1) {
            span.classList.add("completed");
        }

        // 우선순위 선택
        const priority = document.createElement("select");

        ["높음", "보통", "낮음"].forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            priority.appendChild(option);
        });

        priority.value = todo.priority;

        priority.onchange = () => {
            changePriority(todo.id, priority.value);
        };

        // 수정 버튼
        const editBtn = document.createElement("button");
        editBtn.textContent = "수정";
        editBtn.onclick = () => editTodo(todo.id, todo.title);

        // 삭제 버튼
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "삭제";
        deleteBtn.className = "delete-btn";
        deleteBtn.onclick = () => deleteTodo(todo.id);

        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(priority);
        li.appendChild(editBtn);
        li.appendChild(deleteBtn);

        list.appendChild(li);
    });
}

// CREATE - 할 일 등록
async function addTodo() {
    const input = document.getElementById("todoInput");
    const priority = document.getElementById("priorityInput").value;
    const title = input.value.trim();

    if (!title) {
        alert("할 일을 입력하세요.");
        return;
    }

    const response = await fetch("/api/todos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title, priority})
    });

    if (!response.ok) {
        alert("등록 실패");
        return;
    }

    input.value = "";
    await loadTodos();
}

// UPDATE - 제목 수정
async function editTodo(id, oldTitle) {
    const title = prompt("할 일을 수정하세요", oldTitle);

    if (title === null) return;

    if (!title.trim()) {
        alert("내용을 입력하세요.");
        return;
    }

    const response = await fetch(`/api/todos/${id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title: title.trim()})
    });

    if (!response.ok) {
        alert("수정 실패");
        return;
    }

    await loadTodos();
}

// UPDATE - 완료 상태 변경
async function changeCompleted(id, completed) {
    const response = await fetch(`/api/todos/${id}/complete`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({completed})
    });

    if (!response.ok) {
        alert("완료 상태 변경 실패");
    }

    await loadTodos();
}

// UPDATE - 우선순위 변경
async function changePriority(id, priority) {
    const response = await fetch(`/api/todos/${id}/priority`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({priority})
    });

    if (!response.ok) {
        alert("우선순위 변경 실패");
    }

    await loadTodos();
}

// DELETE - 삭제
async function deleteTodo(id) {
    if (!confirm("정말 삭제하시겠습니까?")) return;

    const response = await fetch(`/api/todos/${id}`, {
        method: "DELETE"
    });

    if (!response.ok) {
        alert("삭제 실패");
        return;
    }

    await loadTodos();
}

// 페이지 시작 시 목록 조회
loadTodos();
