function addFilesToList(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);

    // Перевірка, чи є вибрані файли
    if (input.files.length === 0) {
        return; // Якщо файли не вибрані, нічого не робимо
    }

    // Додаємо вибрані файли до списку
    Array.from(input.files).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file.name;

        // Додавання кнопки для видалення файлу
        const removeButton = document.createElement('button');
        removeButton.textContent = "×";
        removeButton.classList.add("remove-file");
        removeButton.onclick = () => {
            li.remove();
            removeFileFromInput(input, file.name);
        };

        // Додаємо кнопку праворуч від назви файлу
        li.appendChild(removeButton);
        list.appendChild(li);
    });
}

function removeFileFromInput(input, fileName) {
    const dt = new DataTransfer();
    Array.from(input.files)
        .filter((file) => file.name !== fileName)
        .forEach((file) => dt.items.add(file));
    input.files = dt.files;
}

document.addEventListener("DOMContentLoaded", function () {
    // Додаємо вже завантажені файли в список
    const existingMediaInput = document.getElementById("media-upload");
    const existingObjectInput = document.getElementById("object-upload");
    const existingPreviewInput = document.getElementById("preview-upload");

    // Додаємо існуючі медіафайли
    if (existingMediaInput) {
        existingMediaInput.addEventListener("change", function () {
            addFilesToList("media-upload", "media-files-list");
        });
    }

    // Додаємо існуючі 3D об'єкти
    if (existingObjectInput) {
        existingObjectInput.addEventListener("change", function () {
            addFilesToList("object-upload", "object-3d-files-list");
        });
    }

    // Додаємо існуючі прев'ю
    if (existingPreviewInput) {
        existingPreviewInput.addEventListener("change", function () {
            addFilesToList("preview-upload", "preview-files-list");
        });
    }

    // Додаємо вже завантажені файли
    document.querySelectorAll(".remove-file").forEach(button => {
        button.addEventListener("click", function () {
            const listItem = this.parentElement;
            listItem.style.display = "none";
            listItem.classList.add("hidden-file");
            listItem.querySelector("input[type=hidden]").remove();  // Видаляємо hidden input, щоб файл не відправлявся
        });
    });

    // Видаляємо приховані файли перед відправленням
    document.querySelector("form").addEventListener("submit", function () {
        document.querySelectorAll(".hidden-file").forEach(item => {
            item.remove(); // Видаляємо приховані файли перед надсиланням форми
        });
    });
});
