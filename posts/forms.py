from django import forms
from posts.models import Post
from django.core.exceptions import ValidationError
from PIL import Image


class PostForm(forms.ModelForm):
    media_files = forms.FileField(required=False)
    object_3d_files = forms.FileField(required=False)
    preview_image = forms.FileField(required=False)
    title = forms.CharField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опис'}))
    category = forms.ChoiceField(
        choices=Post.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Категорія"
    )

    class Meta:
        model = Post
        fields = ['title', 'description', 'preview_image', 'media_files', 'object_3d_files']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва поста'}),
            'preview_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Назва',
            'description': 'Опис',
            'preview_image': 'Прев\'ю',
            'media_files': 'Медіафайли',
            'object_3d_files': '3D файли',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Назва є обов'язковою.")
        if len(title) > 50:
            raise ValidationError("Назва не повинна перевищувати 50 символів.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise ValidationError("Опис є обов'язковим.")
        if len(description) > 3000:
            raise ValidationError("Опис не повинен перевищувати 3000 символів.")
        return description

    def clean_media_files(self):
        media_files = self.files.getlist('media_files')
        if not media_files:
            raise ValidationError("Медіафайли є обов'язковими.")
        if len(media_files) > 10:
            raise ValidationError("Максимальна кількість медіафайлів - 10.")

        image_count = 0
        video_count = 0
        for file in media_files:
            if file.content_type.startswith('image/'):
                if file.name.endswith(('jpg', 'jpeg', 'png')):
                    image_count += 1
                else:
                    raise ValidationError("Медіафайли повинні бути у форматах JPG, PNG, MP4.")
            elif file.content_type.startswith('video/'):
                if file.name.endswith('mp4'):
                    video_count += 1
                else:
                    raise ValidationError("Відео мають бути у форматі MP4.")
            else:
                raise ValidationError("Допустимі лише зображення та відео.")

        if image_count > 10:
            raise ValidationError("Максимум 10 зображень.")
        if video_count > 5:
            raise ValidationError("Максимум 5 відео.")

        return media_files

    def clean_preview_image(self):
        preview_image = self.cleaned_data.get('preview_image')
        if not preview_image:
            raise ValidationError("Прев'ю є обов'язковим.")

        try:
            img = Image.open(preview_image)
            img.verify()  # Перевірка, чи файл дійсно є зображенням
        except (IOError, SyntaxError):
            raise ValidationError("Прев'ю має бути у форматі JPG або PNG.")

        if not preview_image.name.lower().endswith(('jpg', 'jpeg', 'png')):
            raise ValidationError("Прев'ю має бути у форматі JPG або PNG.")
        return preview_image

    def clean_object_3d_files(self):
        object_3d_files = self.files.getlist('object_3d_files')
        if not object_3d_files:
            raise ValidationError("Файли 3D об'єктів є обов'язковими.")
        if len(object_3d_files) > 50:
            raise ValidationError("Максимум 50 файлів 3D об'єктів.")

        for file in object_3d_files:
            if not file.name.lower().endswith('.stl'):
                raise ValidationError("Файли 3D об'єктів мають бути у форматі STL.")

        return object_3d_files

