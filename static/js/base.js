// Отримуємо елементи
const micBtn = document.getElementById("micBtn");
const micModal = document.getElementById("micModal");
const closeModal = document.querySelector(".close");
const transcription = document.getElementById("transcription");
const searchInput = document.querySelector(".search-input");
let hoverTimer; // Таймер для ефекту градієнта

// Створюємо об'єкт для розпізнавання мови
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

// Налаштування розпізнавання
recognition.lang = "uk-UA";
recognition.interimResults = true; // Показує проміжні результати
let finalTranscript = "";

// Обробка наведення на кнопку
micBtn.addEventListener("mouseenter", () => {
    hoverTimer = setTimeout(() => {
        micBtn.classList.add("gradient"); // Додаємо градієнтний ефект
    }, 10000); // Чекаємо 3 секунди
});

// Обробка виходу курсора з кнопки
micBtn.addEventListener("mouseleave", () => {
    clearTimeout(hoverTimer); // Скасовуємо таймер
    micBtn.classList.remove("gradient"); // Повертаємо звичайний стиль
});

// Відкриття модального вікна і старт розпізнавання
micBtn.addEventListener("click", function() {
    micModal.style.display = "block";
    transcription.textContent = "Слухаю...";
    finalTranscript = "";
    recognition.start();
});

// Обробка результатів розпізнавання
recognition.onresult = function(event) {
    let interimTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
        let transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
            finalTranscript += transcript;
        } else {
            interimTranscript += transcript;
        }
    }
    transcription.textContent = finalTranscript || interimTranscript;
};

// Завершення запису і автоматичний пошук
recognition.onend = function() {
    if (finalTranscript) {
        searchInput.value = finalTranscript; // Записуємо текст у поле пошуку
        performSearch(finalTranscript); // Виконуємо пошук
    }
    micModal.style.display = "none"; // Закриваємо модальне вікно
};

// Функція для виконання пошуку
function performSearch(query) {
    console.log("Виконується пошук: ", query);
    // Реалізуйте логіку пошуку, наприклад, перенаправлення на сторінку пошуку
    window.location.href = `/search?query=${encodeURIComponent(query)}`;
}

// Закриття модального вікна при натисканні на хрестик
closeModal.addEventListener("click", function() {
    micModal.style.display = "none";
    recognition.stop(); // Зупиняємо розпізнавання голосу
});

// Закриття модального вікна при кліку поза ним
window.onclick = function(event) {
    if (event.target == micModal) {
        micModal.style.display = "none";
        recognition.stop(); // Зупиняємо розпізнавання голосу
    }
};

// Обробка для відкриття/закриття sidebar
$(document).ready(function () {
    $(".menu-toggle").click(function () {
        $("#sidebar").toggleClass("active");
    });
});

