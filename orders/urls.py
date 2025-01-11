from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('order-characteristics/<int:order_id>/<int:file_index>/', views.order_characteristics, name='order_characteristics'),

    path('cart/', views.view_cart, name='cart'),
]
