import os
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from posts.models import Post
from .forms import CustomUserLoginForm, ProfileEditForm, RegistrationForm, PasswordResetRequestForm, \
    PasswordResetCodeForm, PasswordResetForm
from .models import Notification, User
from django.core.mail import send_mail
import random
import string
from django.conf import settings


def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Отримуємо дані з форми
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            country = form.cleaned_data['country']
            password = form.cleaned_data['password']

            # Генерація коду підтвердження
            confirmation_code = generate_confirmation_code()

            # Зберігаємо код підтвердження в сесії
            request.session['confirmation_code'] = confirmation_code

            # Надсилаємо код на пошту користувача
            send_mail(
                'Підтвердження реєстрації',
                f'Ваш код підтвердження: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Зберігаємо форму в сесії, щоб потім використати її для створення користувача
            request.session['registration_data'] = {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'country': country,
                'password': password,
            }

            # Перенаправляємо на сторінку введення коду підтвердження
            return redirect(reverse('confirm_email'))
    else:
        form = RegistrationForm()

    return render(request, 'users_html/register.html', {'form': form})


def confirm_email(request):
    if request.method == 'POST':
        # Отримуємо 6 цифр коду та об'єднуємо їх у один рядок
        confirmation_code = "".join([
            request.POST.get(f'code{i}', '') for i in range(1, 7)
        ])

        # Вивід коду у термінал для відлагодження
        print(f"Введений код: {confirmation_code}")
        print(f"Очікуваний код: {request.session.get('confirmation_code')}")

        if confirmation_code == request.session.get('confirmation_code'):
            # Отримуємо дані реєстрації
            registration_data = request.session.get('registration_data')

            if not registration_data:
                return redirect('register')  # Якщо немає даних, повертаємо до реєстрації

            # Створюємо користувача
            User = get_user_model()
            user = User.objects.create_user(
                email=registration_data['email'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                phone_number=registration_data['phone_number'],
                country=registration_data['country'],
                password=registration_data['password'],
            )

            # Генеруємо випадковий аватар
            avatars_path = os.path.join(settings.MEDIA_ROOT, 'avatars_registration')
            avatar_files = os.listdir(avatars_path)
            if avatar_files:
                random_avatar = random.choice(avatar_files)
                user.avatar = f'avatars_registration/{random_avatar}'

            user.is_active = True  # Активуємо користувача
            user.save()

            # Видаляємо код підтвердження
            del request.session['confirmation_code']
            del request.session['registration_data']

            # Автоматичний вхід
            login(request, user)

            return redirect('home')

        else:
            return render(request, 'users_html/confirm_email.html', {'error': 'Невірний код підтвердження'})

    return render(request, 'users_html/confirm_email.html')



def usage_agreement(request):
    return render(request, 'users_html/usage_agreement.html')


def user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                form.add_error(None, 'Неправильний логін або пароль.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'users_html/login.html', {'form': form})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile'))
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'users_html/edit_profile.html', {'form': form})


@login_required(login_url='/login/')
def user_profile(request):
    user = request.user
    posts = Post.objects.filter(author=user)  # Отримуємо пости, які створив користувач
    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'users_html/user_profile.html', context)



@login_required(login_url='/login/')
def user_profile_by_icon(request, user_id):
    user = get_object_or_404(User, id=user_id)
    posts = Post.objects.filter(author=user)
    context = {
        'user': user,
        'posts': posts,
    }
    return render(request, 'users_html/user_profile_by_icon.html', context)


@login_required(login_url='/login/')
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect(reverse('home'))
    return redirect('user_profile')


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect('login')


def send_reset_code(user):
    """Відправляє код відновлення на електронну пошту"""
    user.generate_reset_code()
    send_mail(
        'Відновлення пароля',
        f'Ваш код для відновлення пароля: {user.reset_code}',
        'your-email@gmail.com',
        [user.email],
        fail_silently=False,
    )


def request_password_reset(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)
            send_reset_code(user)
            return redirect("password_reset_code")


    else:
        form = PasswordResetRequestForm()

    return render(request, "users_html/password_reset_request.html", {"form": form})


def verify_reset_code(request):
    if request.method == "POST":
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            # Перевірка правильності коду
            code = form.cleaned_data["code"]
            try:
                # Перевірка, чи є користувач із таким кодом
                user = User.objects.get(reset_code=code, reset_code_expires__gte=now())
                request.session["reset_user_id"] = user.id
                return redirect("password_reset_form")
            except User.DoesNotExist:
                # Якщо користувача не знайдено
                form.add_error("code", "Невірний код підтвердження.")
    else:
        form = PasswordResetCodeForm()

    return render(request, "users_html/password_reset_code.html", {"form": form})



def reset_password(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("request_password_reset")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password"])
            user.reset_code = None
            user.reset_code_expires = None
            user.save()
            return redirect("login")
    else:
        form = PasswordResetForm()

    return render(request, "users_html/password_reset_form.html", {"form": form})


def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users_html/user_notifications.html', {'notifications': notifications})




