
// 서버에서 할 일 목록 가져오기
async function loadTodos() {
    const response = await fetch("/api/todos");
    const todos = await response.json();

    const list = document.getElementById("todoList");
    list.innerHTML = "";

    todos.forEach(todo => {
        const li = document.createElement("li");
        li.textContent = todo.title;
        list.appendChild(li);
    });
}

// 서버에 새로운 할 일 등록하기
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
        body: JSON.stringify({ title: title })
    });

    if (!response.ok) {
        alert("할 일 등록에 실패했습니다.");
        return;
    }

    input.value = "";
    await loadTodos();
}

// 페이지가 열리면 서버에서 목록 조회
loadTodos();
