from django import forms

from orders.models import ServicePricing


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