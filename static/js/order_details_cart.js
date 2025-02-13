document.addEventListener('DOMContentLoaded', function () {
    const deleteOrderBtn = document.getElementById('delete-order-btn');
    const modal = document.getElementById('deleteModal');
    const cancelDelete = document.getElementById('cancelDelete');

    // Відкриваємо модальне вікно при натисканні кнопки
    deleteOrderBtn.addEventListener('click', function () {
        modal.style.display = 'flex'; // Показуємо модальне вікно
    });

    // Закриваємо модальне вікно при натисканні кнопки "Скасувати"
    cancelDelete.addEventListener('click', function () {
        modal.style.display = 'none'; // Приховуємо модальне вікно
    });
});





document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("deleteModalFile");
    const closeModal = modal.querySelector(".close");
    const cancelBtn = modal.querySelector(".cancel-button");

    document.querySelectorAll(".delete-file-button").forEach(button => {
        button.addEventListener("click", function () {
            modal.style.display = "block";
        });
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    cancelBtn.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

