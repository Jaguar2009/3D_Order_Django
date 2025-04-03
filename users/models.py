from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email необхідний для створення користувача')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(email, first_name, last_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Адмін'),
        ('moderator', 'Модератор'),
        ('user', 'Користувач'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    date_joined = models.DateTimeField(default=timezone.now)
    is_sanctuary_enabled = models.BooleanField(default=False, verbose_name="Фільтр коментарів (Убежище)")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_expires = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def generate_reset_code(self):
        """Генерує одноразовий код для відновлення пароля."""
        self.reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        self.reset_code_expires = timezone.now() + timezone.timedelta(minutes=10)
        self.save()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст повідомлення")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата створення")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    def __str__(self):
        return f"Повідомлення для {self.user.first_name}: {self.title}"


class UserBan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bans")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення бану")
    banned_until = models.DateTimeField(verbose_name="Час закінчення бану")
    reason = models.TextField(verbose_name="Причина бану", blank=True, null=True)

    def __str__(self):
        return f"Бан для {self.user.email} до {self.banned_until}"