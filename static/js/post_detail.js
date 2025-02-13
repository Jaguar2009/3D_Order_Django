let currentIndex = 0;
const items = document.querySelectorAll('.carousel-item');
const totalItems = items.length;

document.getElementById('prevBtn').addEventListener('click', () => {
  currentIndex = (currentIndex - 1 + totalItems) % totalItems;
  updateCarousel();
});

document.getElementById('nextBtn').addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % totalItems;
  updateCarousel();
});

function updateCarousel() {
  const offset = -currentIndex * 100;
  document.querySelector('.carousel-inner').style.transform = `translateX(${offset}%)`;
}



// Додаємо слухачі подій для вкладок
document.querySelectorAll('.tab-button').forEach(button => {
  button.addEventListener('click', (e) => {
    // Видаляємо клас 'active' від усіх кнопок та вкладок
    document.querySelectorAll('.tab-button').forEach(button => button.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    // Додаємо клас 'active' до вибраної вкладки та її контенту
    e.target.classList.add('active');
    const targetPane = document.getElementById(e.target.getAttribute('data-target'));
    targetPane.classList.add('active');
  });
});

// Дефолтно відкриваємо вкладку "Деталі моделі"
document.querySelector('.tab-button.active').click();

document.getElementById("openModal").addEventListener("click", function() {
  document.getElementById("deleteModal").style.display = "flex";
});

document.getElementById("closeModal").addEventListener("click", function() {
  document.getElementById("deleteModal").style.display = "none";
});


document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".reply-button").forEach(button => {
            button.addEventListener("click", function () {
                let commentId = this.getAttribute("data-comment-id");
                let replyForm = document.getElementById("reply-form-" + commentId);
                if (replyForm.style.display === "none") {
                    replyForm.style.display = "block";
                } else {
                    replyForm.style.display = "none";
                }
            });
        });
    });


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".cube-button").forEach(button => {
        button.addEventListener("click", function () {
            let commentId = this.getAttribute("data-comment-id");
            let form = this.closest(".cube-form");  // Знаходимо форму
            let cubeCount = this.querySelector(".cube-count");  // Лічильник кубів
            let url = form.getAttribute("action");  // URL для запиту

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': form.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: JSON.stringify({ comment_id: commentId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cubeCount.textContent = data.cubes;  // Оновлення лічильника
                }
            })
            .catch(error => console.error("Помилка:", error));
        });
    });
});



document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".delete-comment-button");
    const modal = document.getElementById("deleteCommentModal");
    const closeModalButton = document.querySelector(".close-modal");
    const cancelDeleteButton = document.querySelector(".cancel-delete-button");
    const form = document.getElementById("delete-comment-form");
    const commentIdInput = document.getElementById("comment_id");

    deleteButtons.forEach(button => {
        button.addEventListener("click", function () {
            const commentId = this.getAttribute("data-comment-id");
            commentIdInput.value = commentId; // Передаємо id в прихований інпут
            modal.style.display = "flex"; // Відкриваємо модальне вікно
        });
    });

    // Закрити модальне вікно
    closeModalButton.addEventListener("click", function () {
        modal.style.display = "none";
    });

    cancelDeleteButton.addEventListener("click", function () {
        modal.style.display = "none";
    });
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-reply-button").forEach(button => {
        button.addEventListener("click", function () {
            let replyId = this.getAttribute("data-reply-id");
            let replyForm = document.getElementById("delete-reply-form");
            let modal = document.getElementById("deleteReplyModal");
            let replyInput = document.getElementById("reply_id");

            // Встановлюємо ID відповіді в схований інпут
            replyInput.value = replyId;

            // Відкриваємо модальне вікно
            modal.style.display = "block";
        });
    });

    // Закриваємо модальне вікно
    document.querySelectorAll(".close-modal, .cancel-delete-button").forEach(button => {
        button.addEventListener("click", function () {
            let modal = document.getElementById("deleteReplyModal");
            modal.style.display = "none";
        });
    });
});

