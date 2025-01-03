from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('order-characteristics/<int:order_id>/<int:file_index>/', views.order_characteristics, name='order_characteristics'),
    path('cart/', views.view_cart, name='cart'),  # Для перегляду кошика
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # Для видалення товару з кошика
]
