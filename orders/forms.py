from django import forms
from django.core.exceptions import ValidationError
from .models import Order, OrderFile, ModelCharacteristics


# Форма для замовлення
class OrderForm(forms.ModelForm):
    files = forms.FileField(required=False)
    title = forms.CharField(required=False)
    comments = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Order
        fields = ['title', 'delivery_time', 'comments']
        widgets = {
            'delivery_time': forms.Select(choices=Order.DELIVERY_TIME_CHOICES),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Назва замовлення є обов'язковою.")
        if len(title) > 50:
            raise ValidationError("Назва не повинна перевищувати 50 символів.")
        return title

    def clean_comments(self):
        comments = self.cleaned_data.get('comments')
        if not comments:
            raise ValidationError("Коментар є обов'язковим.")
        if len(comments) > 3000:
            raise ValidationError("Коментар не може бути довшим за 3000 символів.")
        return comments

    def clean_files(self):
        files = self.files.getlist('media_files')
        if not files:
            raise ValidationError("Файли 3D об'єктів є обов'язковими.")
        if len(files) > 50:
            raise ValidationError("Максимум 50 файлів 3D об'єктів.")

        for file in files:
            if not file.name.lower().endswith('.stl'):
                raise ValidationError("Файли 3D об'єктів мають бути у форматі STL.")
        return files

# Форма для завантаження файлів
class OrderFileForm(forms.ModelForm):
    class Meta:
        model = OrderFile
        fields = ['file', 'file_name']


class ModelCharacteristicsForm(forms.ModelForm):
    size = forms.FloatField(required=False)
    copies = forms.FloatField(required=False)
    class Meta:
        model = ModelCharacteristics
        fields = ['material_type', 'material_color', 'size', 'resolution', 'support_structure', 'post_processing',
                  'copies']

    # Валідація для обов'язкових полів
    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size <= 0:
            raise forms.ValidationError("Розмір має бути додатнім числом.")
        return size

    def clean_copies(self):
        copies = self.cleaned_data.get('copies')
        if copies <= 0:
            raise forms.ValidationError("Кількість копій повинна бути більше нуля.")
        return copies

    # Додавання кастомних повідомлень для кожного поля
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material_type'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['material_color'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['size'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['resolution'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['support_structure'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['post_processing'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
        self.fields['copies'].error_messages = {
            'required': 'Це поле є обов\'язковим!',
        }
