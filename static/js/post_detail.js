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
