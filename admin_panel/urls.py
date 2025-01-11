from django.urls import path
from . import views

urlpatterns = [
    path('admin-orders/', views.admin_orders, name='admin_orders'),
]
