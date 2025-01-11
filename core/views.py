from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    context = {
        'user': request.user,
    }
    return render(request, 'core_html/home.html', context)