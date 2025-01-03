from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

import os
import random
from django.conf import settings
from users.models import User


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
        if not phone_number:
            raise ValidationError("Це поле є обов'язковим.")

        # Перевірка номера телефону
        if len(phone_number) < 10:
            raise ValidationError("Номер телефону повинен містити щонайменше 10 цифр.")

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
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
            raise ValidationError("Підтвердження пароля повинно містити щонайменше 8 символів.")  # Помилка, якщо символів менше

        if password != confirm_password:
            raise ValidationError("Паролі не збігаються.")  # Помилка, якщо паролі не збігають

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



    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        avatars_path = os.path.join(settings.MEDIA_ROOT, 'avatars_registration')
        avatar_files = os.listdir(avatars_path)
        random_avatar = random.choice(avatar_files)

        # Додайте аватар користувачу
        user.avatar = f'avatars_registration/{random_avatar}'
        if commit:
            user.save()
        return user
