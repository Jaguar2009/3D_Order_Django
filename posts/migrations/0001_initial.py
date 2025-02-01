# Generated by Django 5.1.4 on 2024-12-30 20:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Назва')),
                ('description', models.TextField(verbose_name='Опис')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('preview_image', models.ImageField(blank=True, null=True, upload_to='post_previews/', verbose_name="Прев'ю")),
                ('media_files', models.FileField(blank=True, null=True, upload_to='post_media/', verbose_name='Медіа файли')),
                ('object_3d_files', models.FileField(blank=True, null=True, upload_to='post_3d_objects/', verbose_name="Файли 3D об'єктів")),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
        ),
    ]
