from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomUserLoginForm, ProfileEditForm, RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('home'))
    else:
        form = RegistrationForm()
    return render(request, 'users_html/register.html', {'form': form})


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
            return redirect(reverse('home'))
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'tasks_html/edit_profile.html', {'form': form})

@login_required(login_url='/login/')
def user_profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'tasks_html/user_profile.html', context)

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

