from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('order-characteristics/<int:order_id>/<int:file_index>/', views.order_characteristics, name='order_characteristics'),

    path('cart/', views.view_cart, name='cart'),
    path('user-orders/', views.user_orders, name='user_orders'),
    path('order-details/<int:order_id>/', views.order_details, name='order-details'),
    path('order/<int:order_id>/pay/', views.pay_order, name='pay_order'),

]
