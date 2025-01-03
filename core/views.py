from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    context = {
        'user': request.user,  # Передаємо об'єкт користувача
    }
    return render(request, 'core_html/home.html', context)