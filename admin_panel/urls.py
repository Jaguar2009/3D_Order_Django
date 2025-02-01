from django.urls import path
from . import views

urlpatterns = [
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-order-details/<int:order_id>/', views.admin_order_details, name='admin_order_details'),
    path('materials/create/', views.create_material, name='create_material'),
    path('materials/admin/', views.admin_materials, name='admin_materials'),

]
