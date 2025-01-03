function addFilesToList(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);
    list.innerHTML = ''; // очищаємо список перед додаванням

    Array.from(input.files).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file.name;

        const removeButton = document.createElement('button');
        removeButton.textContent = "×";
        removeButton.classList.add("remove-file");
        removeButton.onclick = () => {
            li.remove();
            removeFileFromInput(input, file.name);
        };

        li.appendChild(removeButton);
        list.appendChild(li);
    });
}

function removeFileFromInput(input, fileName) {
    const dt = new DataTransfer();
    Array.from(input.files)
        .filter(file => file.name !== fileName)
        .forEach(file => dt.items.add(file));
    input.files = dt.files;
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("create-order-form");
    const titleInput = document.getElementById("title");
    const commentsInput = document.getElementById("comments");
    const fieldsToPersist = ["title", "comments"];

    // Відновлення текстових полів з localStorage
    fieldsToPersist.forEach((field) => {
        const inputElement = document.getElementById(field);
        const savedValue = localStorage.getItem(field);
        if (savedValue) inputElement.value = savedValue;

        inputElement.addEventListener("input", () => {
            localStorage.setItem(field, inputElement.value);
        });
    });

    window.addFilesToList = addFilesToList;
});
