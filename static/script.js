
let allTodos = [];

// 서버에서 로그인 사용자의 할 일 가져오기
async function loadTodos() {
    try {
        const response = await fetch("/api/todos");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            throw new Error("목록 조회 실패");
        }

        allTodos = await response.json();
        renderTodos();

    } catch (error) {
        console.error(error);
        alert("할 일 목록을 불러오지 못했습니다.");
    }
}

// 검색 / 필터 / 정렬 / 통계
function renderTodos() {
    const keyword = document.getElementById("searchInput")
        .value.trim().toLowerCase();

    const status = document.getElementById("statusFilter").value;
    const sort = document.getElementById("sortOrder").value;

    // 통계
    const total = allTodos.length;

    const done = allTodos.filter(todo =>
        todo.completed === 1
    ).length;

    document.getElementById("totalCount").textContent = total;
    document.getElementById("doneCount").textContent = done;
    document.getElementById("activeCount").textContent = total - done;

    // 검색
    let visibleTodos = allTodos.filter(todo =>
        todo.title.toLowerCase().includes(keyword)
    );

    // 필터
    if (status === "active") {
        visibleTodos = visibleTodos.filter(todo =>
            todo.completed === 0
        );
    } else if (status === "done") {
        visibleTodos = visibleTodos.filter(todo =>
            todo.completed === 1
        );
    }

    // 정렬
    const priorityRank = {
        "높음": 0,
        "보통": 1,
        "낮음": 2
    };

    visibleTodos.sort((a, b) => {
        if (sort === "old") {
            return a.id - b.id;
        }

        if (sort === "priority") {
            return priorityRank[a.priority]
                 - priorityRank[b.priority]
                 || b.id - a.id;
        }

        return b.id - a.id;
    });

    const list = document.getElementById("todoList");
    list.innerHTML = "";

    document.getElementById("emptyMessage").hidden =
        visibleTodos.length > 0;

    visibleTodos.forEach(todo => {
        const li = document.createElement("li");
        li.className = "todo-item";

        // 완료 체크박스
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = todo.completed === 1;
        checkbox.setAttribute("aria-label", "완료 여부");

        checkbox.onchange = () =>
            changeCompleted(todo.id, checkbox.checked);

        // 제목
        const span = document.createElement("span");
        span.textContent = todo.title;
        span.className = "todo-title";

        if (todo.completed === 1) {
            span.classList.add("completed");
        }

        // 우선순위
        const priority = document.createElement("select");
        priority.className = "priority-select";
        priority.setAttribute("aria-label", "우선순위");

        ["높음", "보통", "낮음"].forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            priority.appendChild(option);
        });

        priority.value = todo.priority;

        priority.onchange = () =>
            changePriority(todo.id, priority.value);

        // 수정
        const editBtn = document.createElement("button");
        editBtn.textContent = "수정";
        editBtn.className = "edit-btn";

        editBtn.onclick = () =>
            editTodo(todo.id, todo.title);

        // 삭제
        const deleteBtn = document.createElement("button");
        deleteBtn.textContent = "삭제";
        deleteBtn.className = "delete-btn";

        deleteBtn.onclick = () =>
            deleteTodo(todo.id);

        li.appendChild(checkbox);
        li.appendChild(span);
        li.appendChild(priority);
        li.appendChild(editBtn);
        li.appendChild(deleteBtn);

        list.appendChild(li);
    });
}

// 등록
async function addTodo() {
    const input = document.getElementById("todoInput");
    const title = input.value.trim();

    const priority = document.getElementById("priorityInput").value;

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

// 수정
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

// 완료 상태 변경
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

// 우선순위 변경
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

// 삭제
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

// 이벤트 연결
document.getElementById("todoForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();
        await addTodo();
    }
);

document.getElementById("searchInput")
    .addEventListener("input", renderTodos);

document.getElementById("statusFilter")
    .addEventListener("change", renderTodos);

document.getElementById("sortOrder")
    .addEventListener("change", renderTodos);

// 최초 실행
loadTodos();
