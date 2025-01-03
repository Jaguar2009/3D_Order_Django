function updateFileList(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);
    list.innerHTML = ''; // Очищаємо список

    Array.from(input.files).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file.name;
        list.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("create-post-form");
    const titleInput = document.getElementById("title");
    const descriptionInput = document.getElementById("description");
    const fieldsToPersist = ["title", "description"];

    // Відновлення текстових полів з localStorage
    fieldsToPersist.forEach((field) => {
        const inputElement = document.getElementById(field);
        const savedValue = localStorage.getItem(field);
        if (savedValue) inputElement.value = savedValue;

        inputElement.addEventListener("input", () => {
            localStorage.setItem(field, inputElement.value);
        });
    });

    // Функція для оновлення списку файлів
    const addFilesToList = (inputId, listId) => {
        const input = document.getElementById(inputId);
        const list = document.getElementById(listId);
        const files = Array.from(input.files);

        list.innerHTML = ''; // очищуємо список перед додаванням

        files.forEach((file) => {
            const listItem = document.createElement("li");
            listItem.textContent = file.name;

            const removeButton = document.createElement("button");
            removeButton.textContent = "×";
            removeButton.classList.add("remove-file");
            removeButton.onclick = () => {
                listItem.remove();
                removeFileFromInput(input, file.name);
            };

            listItem.appendChild(removeButton);
            list.appendChild(listItem);
        });
    };

    const removeFileFromInput = (input, fileName) => {
        const dt = new DataTransfer();
        Array.from(input.files)
            .filter((file) => file.name !== fileName)
            .forEach((file) => dt.items.add(file));
        input.files = dt.files;
    };

    // Застосуємо стилі через JS (переконаємося, що елементи мають ширину 100%)
    const inputs = document.querySelectorAll('.post-title, .post-description, .publish-button, .upload-label input[type="file"]');
    inputs.forEach(input => {
        input.style.width = '100%';
    });

    window.addFilesToList = addFilesToList;
});

