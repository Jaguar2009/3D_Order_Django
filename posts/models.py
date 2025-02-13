from django.db import models
from users.models import User

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('home', 'Для дому'),
        ('hobby', 'Хобі та творчість'),
        ('kids', 'Для дітей'),
        ('gadgets', 'Гаджети та аксесуари'),
        ('tools', 'Інструменти та функціональні речі'),
        ('printers', 'Для 3D-принтерів'),
        ('other', 'Інше'),
    ]
    title = models.CharField(max_length=200, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категорія"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    preview_image = models.ImageField(upload_to='post_previews/', verbose_name="Прев'ю", blank=True, null=True)
    cubes = models.PositiveIntegerField(default=0, verbose_name="Куби")
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title


class MediaFile(models.Model):
    post = models.ForeignKey(Post, related_name='media_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_media/', verbose_name="Медіа файли")


class Object3DFile(models.Model):
    post = models.ForeignKey(Post, related_name='object_3d_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_3d_objects/', verbose_name="Файли 3D об'єктів")


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Зміст коментаря")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    cubes = models.PositiveIntegerField(default=0, verbose_name="Куби")
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True, verbose_name="Куби на коментарях")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="Батьківський коментар")

    def __str__(self):
        return f"Коментар від {self.author.first_name} на {self.post.title}"
