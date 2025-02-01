from django import forms
from django.core.exceptions import ValidationError
from .models import Order, OrderFile, ModelCharacteristics, ServicePricing


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

class OrderFileForm(forms.ModelForm):
    class Meta:
        model = OrderFile
        fields = ['file', 'file_name']


class ModelCharacteristicsForm(forms.ModelForm):
    size = forms.FloatField(required=False)
    copies = forms.FloatField(required=False)
    filling = forms.FloatField(required=False)
    color = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = ModelCharacteristics
        fields = ['material', 'size', 'resolution', 'support_structure', 'post_processing',
                  'copies', 'filling']

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size is None:
            raise forms.ValidationError("Поле не може бути пустим.")
        if size <= 0:
            raise forms.ValidationError("Розмір має бути додатнім числом.")
        if size > 200:
            raise forms.ValidationError("Максимальне значення розміру — 200.")
        return size

    def clean_copies(self):
        copies = self.cleaned_data.get('copies')
        if copies is None:
            raise forms.ValidationError("Це поле є обов'язковим.")
        if copies <= 0:
            raise forms.ValidationError("Кількість копій повинна бути більше нуля.")
        if not float(copies).is_integer():
            raise forms.ValidationError("Кількість копій повинна бути цілим числом.")
        return int(copies)

    def clean_filling(self):
        filling = self.cleaned_data.get('filling')
        if filling is None:
            raise forms.ValidationError("Це поле є обов'язковим.")
        if filling <= 0:
            raise forms.ValidationError("Заповнення повинно бути додатнім числом.")
        if filling > 100:
            raise forms.ValidationError("Максимальне значення заповнення — 100.")
        return filling

