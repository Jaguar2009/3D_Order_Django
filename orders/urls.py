from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order, name='create_order'),
    path('order-characteristics/<int:order_id>/<int:file_index>/', views.order_characteristics, name='order_characteristics'),

    path('cart/', views.view_cart, name='cart'),
    path('user-orders/', views.user_orders, name='user_orders'),
    path('order-details/<int:order_id>/', views.order_details, name='order-details'),
    path('order/<int:order_id>/pay/', views.pay_order, name='pay_order'),

    path('order/<int:order_id>/', views.order_details_cart, name='order_details_cart'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),

    path('edit_order_file/<int:order_id>/<int:file_id>/', views.edit_order_file, name='edit_order_file'),
    path('edit_characteristics/<int:order_id>/<int:file_id>/', views.edit_model_characteristics, name='edit_characteristics'),
    path('delete_order_file/<int:order_id>/<int:file_id>/', views.delete_order_file, name='delete_order_file'),

    path('order/<int:order_id>/upload-files/', views.upload_order_files, name='upload_order_files'),
    path('order-characteristics-add/<int:order_id>/<int:file_index>/', views.order_characteristics_add, name='order_characteristics_add'),

    path('repeat_order/<int:order_id>/', views.repeat_order, name='repeat_order'),
]
