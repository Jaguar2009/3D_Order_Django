from django import forms
from django.core.exceptions import ValidationError

from orders.models import ServicePricing
from users.models import User


class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea, label="Причина відмови")

class MaterialForm(forms.ModelForm):
    class Meta:
        model = ServicePricing
        fields = ['parameter_name', 'parameter_value', 'color']
        labels = {
            'parameter_name': 'Назва матеріалу',
            'parameter_value': 'Ціна за метр',
            'color': 'Колір',
        }
        widgets = {
            'parameter_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parameter_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_parameter_value(self):
        value = self.cleaned_data['parameter_value']
        if value <= 0:
            raise forms.ValidationError("Ціна має бути більше нуля.")
        return value

class MaterialEditForm(forms.ModelForm):
    class Meta:
        model = ServicePricing
        fields = ['parameter_name', 'parameter_value', 'color']
        labels = {
            'parameter_name': 'Назва матеріалу',
            'parameter_value': 'Ціна за метр',
            'color': 'Колір',
        }
        widgets = {
            'parameter_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parameter_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_parameter_value(self):
        value = self.cleaned_data['parameter_value']
        if value <= 0:
            raise forms.ValidationError("Ціна має бути більше нуля.")
        return value


class ModeratorForm(forms.Form):
    email = forms.EmailField(label="Email користувача", required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            raise ValidationError("Раб Божого з такою поштою не існує.")
        if user.role == 'admin':
            raise ValidationError("Не можна змінити роль адміністратора на модератора.")

        return email