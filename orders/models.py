from django.db import models
from users.models import User
from django.utils import timezone
from decimal import Decimal


class ServicePricing(models.Model):
    PARAMETER_TYPES = [
        ('material', 'Матеріал'),
        ('post_processing', 'Постобробка'),
        ('urgency', 'Терміновість'),
        ('quality', 'Якість'),
    ]

    parameter_type = models.CharField(
        max_length=20,
        choices=PARAMETER_TYPES,
        verbose_name="Тип параметра",
        default="material"
    )
    parameter_name = models.CharField(max_length=50, verbose_name="Назва параметра", default="None")
    parameter_value = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Значення (ціна або множник)",
        default=0
    )
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Колір")

    def __str__(self):
        return f"{self.parameter_name} - {self.parameter_value} {self.color if self.color else ''}"

    @staticmethod
    def get_price(parameter_type: str, parameter_name: str) -> float:
        """Отримати ціну або множник за типом та назвою параметра."""
        try:
            pricing = ServicePricing.objects.get(parameter_type=parameter_type, parameter_name=parameter_name)
            return pricing.parameter_value
        except ServicePricing.DoesNotExist:
            raise ValueError(f"Ціна або множник для '{parameter_type}' -> '{parameter_name}' не знайдено!")


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
    material = models.ForeignKey(ServicePricing, on_delete=models.SET_NULL, null=True, blank=True,
                                 limit_choices_to={'parameter_type': 'material'}, verbose_name="Матеріал")
    size = models.FloatField()
    resolution = models.CharField(max_length=50, choices=[('High', 'Висока'),
                                                          ('Medium', 'Середня'),
                                                          ('Low', 'Низька')],
                                                          default='Medium')
    support_structure = models.CharField(max_length=50, choices=[('With Support', 'З підтримками'),
                                                                 ('Without Support', 'Без підтримок')],
                                                                 default='Without Support')
    post_processing = models.CharField(max_length=50,
                                       choices=[('None', 'Без обробки'),
                                                ('Sandblasting', 'Піскоструминна обробка'),
                                                ('Painting', 'Фарбування'),
                                                ('Pre-Painting', 'Підготовка до фарбування')],
                                                default='None')
    copies = models.PositiveIntegerField(default=1)
    filling = models.FloatField()

    def __str__(self):
        return f"Характеристики для {self.order_file.file_name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Кошик для {self.user.first_name} - {self.order}"


class OrderInfo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Розглядається'),
        ('approved', 'Підтверджено'),
        ('rejected', 'Відхилено'),
    ]

    ORDER_STATUS_CHOICES = [
        ('created', 'Оформлено'),
        ('paid', 'Оплачено'),
        ('printing', 'Друкується'),
        ('shipped', 'Відправлено'),
        ('delivering', 'Доставляється'),
        ('delivered', 'Доставлено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_info_user")
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="order_info")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Час створення")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус"
    )
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default='created', verbose_name="Статус замовлення"
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Загальна вартість")

    def __str__(self):
        return f"Замовлення: {self.order.title} ({self.user.first_name})"

    def calculate_total_cost(self):
        total_cost = 0

        # Отримуємо всі файли замовлення
        for order_file in self.order.files.all():
            try:
                model_characteristics = order_file.characteristics
            except ModelCharacteristics.DoesNotExist:
                continue  # Пропускаємо, якщо немає характеристик

            material_obj = model_characteristics.material  # Отримуємо об'єкт матеріалу
            if not material_obj:
                continue  # Пропускаємо, якщо матеріал не заданий

            copies = model_characteristics.copies
            post_processing = model_characteristics.post_processing
            resolution = model_characteristics.resolution

            # Отримуємо витрати на пластик з OrderApproval
            try:
                order_approval = self.order.order_info.first().approval
                material_consumption = order_approval.plastic_usage_per_file.get(str(order_file.id), 0)
            except (OrderInfo.DoesNotExist, OrderApproval.DoesNotExist):
                material_consumption = 0  # Якщо немає OrderApproval, встановлюємо 0

            # Отримуємо ціну для вибраного матеріалу з урахуванням кольору
            try:
                material_price = ServicePricing.objects.get(
                    parameter_type='material',
                    parameter_name=material_obj.parameter_name,
                    color=material_obj.color  # Фільтрація за кольором
                ).parameter_value
            except ServicePricing.DoesNotExist:
                raise ValueError(
                    f"Ціна для матеріалу '{material_obj.parameter_name}' ({material_obj.color}) не знайдена!")

            # Розрахунок вартості матеріалу
            model_cost = Decimal(material_price) * Decimal(material_consumption)

            # Додаємо ціну постобробки (якщо є)
            if post_processing != 'None':
                model_cost += ServicePricing.get_price('post_processing', post_processing)

            # Додаємо вартість якості
            model_cost += ServicePricing.get_price('quality', resolution)

            # Множимо на кількість копій
            model_cost *= copies

            # Додаємо вартість за терміновість
            urgency_price = ServicePricing.get_price('urgency', self.order.delivery_time)
            model_cost += urgency_price

            # Додаємо до загальної вартості замовлення
            total_cost += model_cost

        # Множимо на кількість замовлень
        total_cost *= self.quantity

        # Зберігаємо вартість у базу даних
        self.total_cost = total_cost
        self.save()

        return total_cost


class OrderApproval(models.Model):
    order_info = models.OneToOneField(OrderInfo, on_delete=models.CASCADE, related_name="approval")
    approval_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата підтвердження")

    plastic_usage_per_file = models.JSONField(default=dict, verbose_name="Використання пластика для кожного файлу (в метрах)")

    def __str__(self):
        return f"Підтверджено: {self.order_info.order.title})"

    def calculate_plastic_usage(self):
        total_plastic_usage = 0
        for file_id, usage in self.plastic_usage_per_file.items():
            total_plastic_usage += usage
        return total_plastic_usage


class OrderRejection(models.Model):
    order_info = models.OneToOneField(OrderInfo, on_delete=models.CASCADE, related_name="rejection")
    rejection_reason = models.TextField(verbose_name="Причина відмови")
    rejection_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата відхилення")

    def __str__(self):
        return f"Відхилено: {self.order_info.order.title} ({self.rejection_reason[:20]}...)"

