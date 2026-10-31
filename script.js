
function addTodo() {
    const input = document.getElementById("todoInput");
    const text = input.value.trim();

    if (text === "") {
        alert("할 일을 입력하세요!");
        return;
    }

    const li = document.createElement("li");
    li.textContent = text;

    document.getElementById("todoList").appendChild(li);

    input.value = "";
}
