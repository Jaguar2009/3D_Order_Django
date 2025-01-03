from django.db import models
from users.models import User
from django.utils import timezone



class MaterialType(models.TextChoices):
    PLA = 'PLA', 'PLA'
    ABS = 'ABS', 'ABS'
    PETG = 'PETG', 'PETG'
    NYLON = 'Nylon', 'Nylon'
    RESIN = 'Resin', 'Resin'
    OTHER = 'Other', 'Інші'


class MaterialColor(models.TextChoices):
    BLACK = 'Black', 'Чорний'
    WHITE = 'White', 'Білий'
    BLUE = 'Blue', 'Синій'
    RED = 'Red', 'Червоний'
    GREEN = 'Green', 'Зелений'
    YELLOW = 'Yellow', 'Жовтий'


class Order(models.Model):
    DELIVERY_TIME_CHOICES = [
        ('Urgent', 'Терміновий'),
        ('Standard', 'Стандартний'),
        ('By Agreement', 'За попереднім погодженням')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    title = models.CharField(max_length=255, verbose_name="Назва замовлення")
    delivery_time = models.CharField(max_length=50, choices=DELIVERY_TIME_CHOICES, default='Standard')
    comments = models.TextField(verbose_name="Коментарі")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Час створення")

    def __str__(self):
        return f"Замовлення: {self.title} ({self.user.first_name})"


class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to='order_files/')
    file_name = models.CharField(max_length=255, verbose_name="Назва файлу")

    def __str__(self):
        return self.file_name


class ModelCharacteristics(models.Model):
    order_file = models.OneToOneField(OrderFile, on_delete=models.CASCADE, related_name="characteristics")
    material_type = models.CharField(max_length=10, choices=MaterialType.choices)
    material_color = models.CharField(max_length=10, choices=MaterialColor.choices)
    size = models.FloatField()
    resolution = models.CharField(max_length=50, choices=[('High', 'Висока'),
                                                          ('Medium', 'Середня'),
                                                          ('Low', 'Низька')])
    support_structure = models.CharField(max_length=50, choices=[('With Support', 'З підтримками'),
                                                                 ('Without Support', 'Без підтримок')])
    post_processing = models.CharField(max_length=50,
                                       choices=[('None', 'Без обробки'),
                                                ('Sandblasting', 'Піскоструминна обробка'),
                                                ('Painting', 'Лакування'),
                                                ('Pre-Painting', 'Підготовка до фарбування')])
    copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Характеристики для {self.order_file.file_name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Кошик для {self.user.first_name} - {self.order}"
