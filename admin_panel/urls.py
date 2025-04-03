from django.urls import path
from . import views

urlpatterns = [
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-order-details/<int:order_id>/', views.admin_order_details, name='admin_order_details'),
    path('materials/create/', views.create_material, name='create_material'),
    path('materials/admin/', views.admin_materials, name='admin_materials'),
    path('delete-material/<int:material_id>/', views.delete_material, name='delete_material'),
    path('material/edit/<int:material_id>/', views.edit_material, name='edit_material'),
    path('users/admin/list', views.user_list, name='user_list'),
    path('admin/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/moderators/', views.moderator_list, name='moderator_list'),
    path('admin/moderator/<int:user_id>/', views.admin_moderator_detail, name='admin_moderator_detail'),
    path('admin/list/', views.admin_list, name='admin_list'),

    #path('admin/detail/<int:user_id>/', views.admin_detail, name='admin_detail'),

]
