from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
    path('profile/', views.user_profile, name='profile'),
    path('logout/', views.user_logout, name='logout'),
    path('notifications/', views.user_notifications, name='user_notifications'),
    path('profile/<int:user_id>/', views.user_profile_by_icon, name='user_profile'),
    path('usage_agreement/', views.usage_agreement, name='usage_agreement'),
    path('confirm-email/', views.confirm_email, name='confirm_email'),  # Додаємо шлях для підтвердження
    path("password-reset/", views.request_password_reset, name="request_password_reset"),
    path("password-reset/code/", views.verify_reset_code, name="password_reset_code"),
    path("password-reset/new/", views.reset_password, name="password_reset_form"),

    ]