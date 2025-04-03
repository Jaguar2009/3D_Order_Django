from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

import os
import random
from django.conf import settings
from users.models import User
from django.utils import timezone


class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={
        'required': 'Це поле є обов\'язковим.',
    })
    password = forms.CharField(widget=forms.PasswordInput, required=True, error_messages={
        'required': 'Це поле є обов\'язковим.',
    })


class ProfileEditForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=[
            ('Ukraine', 'Україна'),
            ('USA', 'США'),
        ],
        required=True,
        error_messages={
            'required': 'Це поле є обов\'язковим.',
        }
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'country', 'avatar']
        error_messages = {
            'email': {
                'required': 'Це поле є обов\'язковим',
            },
            'first_name': {
                'required': 'Це поле є обов\'язковим',
            },
            'last_name': {
                'required': 'Це поле є обов\'язковим',
            },
            'phone_number': {
                'required': 'Це поле є обов\'язковим',
            },
            'country': {
                'required': 'Це поле є обов\'язковим',
            },

        }


    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        user = self.instance

        if not phone_number:
            raise ValidationError("Це поле є обов'язковим.")

        # Перевірка номера телефону
        if len(phone_number) < 10:
            raise ValidationError("Номер телефону повинен містити щонайменше 10 цифр.")

        if user and phone_number != user.phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Цей номер телефону вже зайнятий.")

        # Для українських номерів
        if self.cleaned_data.get('country') == "Ukraine":
            if not phone_number.startswith("+380"):
                raise ValidationError("Номер телефону для України повинен починатися з +380.")
            if len(phone_number) != 13:
                raise ValidationError("Номер телефону для України повинен містити 13 символів.")

        # Для американських номерів
        elif self.cleaned_data.get('country') == "USA":
            if not phone_number.startswith("+1"):
                raise ValidationError("Номер телефону для США повинен починатися з +1.")
            if len(phone_number) != 12:
                raise ValidationError("Номер телефону для США повинен містити 12 символів.")

        return phone_number


    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
        self.fields['phone_number'].required = True
        self.fields['country'].required = True
        self.fields['last_name'].required = True
        self.fields['avatar'].required = False


class RegistrationForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=[
            ('Ukraine', 'Україна'),
            ('USA', 'США'),
        ],
        required=True,
        error_messages={
            'required': 'Це поле є обов\'язковим.',
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        min_length=8,
        error_messages={
            'required': 'Це поле є обов\'язковим.',
            'min_length': 'Пароль повинен містити щонайменше 8 символів.'
        }
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        error_messages={
            'required': 'Це поле є обов\'язковим.'
        }
    )

    agree_to_terms = forms.BooleanField(required=True, label='Угода про користування', error_messages={'required': 'Ця угода є обов\'язковою.'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'country', 'phone_number']
        error_messages = {
            'first_name': {
                'required': 'Це поле є обов\'язковим',
            },
            'last_name': {
                'required': 'Це поле є обов\'язковим',
            },
            'email': {
                'required': 'Це поле є обов\'язковим',
            },
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if len(confirm_password) < 8:
            raise ValidationError("Підтвердження пароля повинно містити щонайменше 8 символів.")
        if password != confirm_password:
            raise ValidationError("Паролі не збігаються.")

        return confirm_password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise ValidationError("Це поле є обов'язковим.")

        # Перевірка номера телефону
        if len(phone_number) < 10:
            raise ValidationError("Номер телефону повинен містити щонайменше 10 цифр.")

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Цей номер телефону вже зайнятий.")

        if self.cleaned_data.get('country') == "Ukraine":
            if not phone_number.startswith("+380"):
                raise ValidationError("Номер телефону для України повинен починатися з +380.")
            if len(phone_number) != 13:
                raise ValidationError("Номер телефону для України повинен містити 13 символів.")

        elif self.cleaned_data.get('country') == "USA":
            if not phone_number.startswith("+1"):
                raise ValidationError("Номер телефону для США повинен починатися з +1.")
            if len(phone_number) != 12:
                raise ValidationError("Номер телефону для США повинен містити 12 символів.")

        return phone_number


    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        user.is_active = False  # Користувач не активний до підтвердження
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Електронна пошта", widget=forms.EmailInput(attrs={"class": "input-field"}))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Перевірка чи існує такий користувач
        if not get_user_model().objects.filter(email=email).exists():
            raise ValidationError("Такої пошти не існує.")
        return email


class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label="Код підтвердження", max_length=6, widget=forms.TextInput(attrs={"class": "input-field"}))


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(label="Новий пароль", widget=forms.PasswordInput(attrs={"class": "input-field"}))
    confirm_password = forms.CharField(label="Підтвердження пароля", widget=forms.PasswordInput(attrs={"class": "input-field"}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("new_password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Паролі не співпадають.")
        return cleaned_data


class BanUserForm(forms.Form):
    banned_until = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now,
        label="Дата закінчення бану"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Введіть причину бану'}),
        max_length=500,
        label="Причина бану"
    )