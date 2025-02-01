from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelform_factory
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderForm, ModelCharacteristicsForm
from .models import Order, OrderFile, ModelCharacteristics, Cart, OrderInfo, ServicePricing
from stl import mesh
import numpy as np
import json


def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            # Створення замовлення
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Збереження файлів
            files = form.cleaned_data['files']
            for file in files:
                OrderFile.objects.create(order=order, file=file, file_name=file.name)

            return redirect('order_characteristics', order_id=order.id, file_index=0)
    else:
        form = OrderForm()

    return render(request, 'order_html/create_order.html', {'form': form})


def order_characteristics(request, order_id, file_index):
    order = Order.objects.get(id=order_id, user=request.user)
    files = order.files.all()

    if file_index < 0 or file_index >= files.count():
        return redirect('some_error_page')

    current_file = files[file_index]

    characteristics = ModelCharacteristics.objects.filter(order_file=current_file).first()

    if request.method == 'POST':
        form = ModelCharacteristicsForm(request.POST, instance=characteristics)
        if form.is_valid():
            characteristics = form.save(commit=False)
            characteristics.order_file = current_file
            characteristics.save()

            if file_index + 1 < files.count():
                return redirect('order_characteristics', order_id=order.id, file_index=file_index + 1)
            else:
                Cart.objects.create(user=request.user, order=order)
                return redirect('cart')
    else:
        form = ModelCharacteristicsForm(instance=characteristics)

    return render(request, 'order_html/order_characteristics.html', {
        'form': form,
        'file_index': file_index,
        'total_files': files.count(),
        'file_name': current_file.file_name,
        'order_id': order.id,
    })


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    if request.method == "POST":
        action = request.POST.get('action')

        if action == 'update':
            for item in cart_items:
                quantity_field_name = f'quantity_{item.id}'
                new_quantity = request.POST.get(quantity_field_name)
                try:
                    new_quantity = int(new_quantity)
                    if new_quantity <= 0:
                        new_quantity = 1
                except (ValueError, TypeError):
                    new_quantity = 1

                if item.quantity != new_quantity:
                    item.quantity = new_quantity
                    item.save()

        elif action == 'purchase':
            selected_orders = request.POST.getlist('selected_orders')
            if selected_orders:
                with transaction.atomic():
                    for cart_item_id in selected_orders:
                        cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
                        OrderInfo.objects.create(
                            user=request.user,
                            order=cart_item.order,
                            quantity=cart_item.quantity
                        )
                        cart_item.delete()

        return redirect('cart')

    return render(request, 'order_html/cart.html', {'cart_items': cart_items})


def user_orders(request):
    # Отримуємо всі замовлення користувача
    orders = OrderInfo.objects.filter(user=request.user)

    context = {
        'orders': orders
    }

    return render(request, 'order_html/user_orders.html', context)


def order_details(request, order_id):
    order_info = get_object_or_404(OrderInfo, id=order_id)
    order = order_info.order  # Отримуємо об'єкт замовлення

    context = {
        'order': order,
        'order_info': order_info,
    }
    return render(request, 'order_html/order_details.html', context)


@csrf_exempt
def pay_order(request, order_id):
    if request.method == "POST":
        order_info = get_object_or_404(OrderInfo, id=order_id)

        # Перевірка, чи статус підтверджено
        if order_info.status != "approved":
            return JsonResponse({"success": False, "error": "Замовлення не підтверджено для оплати."})

        # Перевірка, чи вже оплачено
        if order_info.order_status == "paid":
            return JsonResponse({"success": False, "error": "Це замовлення вже оплачено."})

        # Змінюємо статус на "оплачено"
        order_info.order_status = "paid"
        order_info.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Неправильний метод запиту."})