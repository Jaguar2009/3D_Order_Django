# Generated by Django 5.1.4 on 2025-01-02 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[('home', 'Для дому'), ('hobby', 'Хобі та творчість'), ('kids', 'Для дітей'), ('gadgets', 'Гаджети та аксесуари'), ('tools', 'Інструменти та функціональні речі'), ('printers', 'Для 3D-принтерів'), ('other', 'Інше')], default='other', max_length=20, verbose_name='Категорія'),
        ),
    ]
