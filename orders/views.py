from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelform_factory
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderForm, ModelCharacteristicsForm, OrderEditForm, OrderFileEditForm, ModelCharacteristicsEditForm, \
    ModelCharacteristicsAddForm
from .models import Order, OrderFile, ModelCharacteristics, Cart, OrderInfo, ServicePricing
from stl import mesh
import numpy as np
import json
from rapidfuzz import process

def check_order_permissions(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user and not request.user.is_staff and request.user.role != 'admin':
        return HttpResponseForbidden("У вас немає прав для цього замовлення.")

    return None  # Все в порядку

@login_required(login_url='/users/login/')
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

@login_required(login_url='/users/login/')
def edit_order(request, order_id):
    # Отримуємо замовлення за ID
    order = get_object_or_404(Order, pk=order_id)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    # Створюємо форму для редагування замовлення
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()  # Зберігаємо зміни
            return redirect('order_details_cart', order_id=order.id)  # Перенаправляємо на сторінку з деталями замовлення
    else:
        form = OrderEditForm(instance=order)  # Завантажуємо дані замовлення у форму

    return render(request, 'order_html/edit_order.html', {'form': form, 'order': order})

@login_required(login_url='/users/login/')
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

@login_required(login_url='/users/login/')
def edit_order_file(request, order_id, file_id):
    order_file = get_object_or_404(OrderFile, id=file_id, order_id=order_id)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    if request.method == 'POST':
        form = OrderFileEditForm(request.POST, request.FILES, instance=order_file)
        if form.is_valid():
            updated_order_file = form.save(commit=False)  # Не зберігаємо поки що, щоб змінити назву
            if updated_order_file.file:
                updated_order_file.file_name = updated_order_file.file.name.split('/')[-1]  # Задаємо нову назву файлу
            updated_order_file.save()  # Тепер зберігаємо з новою назвою
            return redirect('edit_characteristics', order_id=order_id, file_id=file_id)  # Перехід до редагування характеристик
    else:
        form = OrderFileEditForm(instance=order_file)

    return render(request, 'order_html/edit_order_file.html', {'form': form, 'order_file': order_file})


@login_required(login_url='/users/login/')
def edit_model_characteristics(request, order_id, file_id):
    order_file = get_object_or_404(OrderFile, id=file_id, order_id=order_id)
    characteristics = get_object_or_404(ModelCharacteristics, order_file=order_file)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    if request.method == 'POST':
        form = ModelCharacteristicsEditForm(request.POST, instance=characteristics)
        if form.is_valid():
            form.save()
            return redirect('order_details_cart', order_id=order_id)  # Перехід на сторінку деталей замовлення
    else:
        form = ModelCharacteristicsEditForm(instance=characteristics)

    return render(request, 'order_html/edit_model_characteristics.html', {'form': form, 'order_file': order_file})

@login_required(login_url='/users/login/')
def delete_order(request, order_id):
    # Перевірка чи користувач має право видаляти замовлення
    order = get_object_or_404(Order, id=order_id)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    # Видалення замовлення
    order.delete()

    # Перенаправлення на сторінку кошика
    return redirect('cart')  # 'cart' - це URL для сторінки кошика

@login_required(login_url='/users/login/')
def delete_order_file(request, order_id, file_id):
    order = get_object_or_404(Order, id=order_id)
    order_file = get_object_or_404(OrderFile, id=file_id, order_id=order_id)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    # Видаляємо характеристики, якщо вони існують
    if order_file.characteristics:
        order_file.characteristics.delete()

    # Видаляємо файл
    order_file.delete()

    # Переадресовуємо на сторінку кошика або іншу необхідну
    return redirect('order_details_cart', order_id=order.id)

@login_required(login_url='/users/login/')
def upload_order_files(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        new_files = []

        for file in files:
            order_file = OrderFile.objects.create(order=order, file=file, file_name=file.name)
            new_files.append(order_file.id)

        # Зберігаємо нові файли в сесії
        request.session['new_file_ids'] = new_files

        # Переадресація на сторінку додавання характеристик
        return redirect('order_characteristics_add', order_id=order.id, file_index=0)

    return render(request, 'order_html/upload_order_files.html', {'order': order})

@login_required(login_url='/users/login/')
def order_characteristics_add(request, order_id, file_index):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden

    # Отримуємо нові файли з сесії
    new_file_ids = request.session.get('new_file_ids', [])
    if not new_file_ids:
        return redirect('some_error_page')  # Якщо сесія порожня або ID файлів немає

    new_files = OrderFile.objects.filter(id__in=new_file_ids, order=order)

    if file_index < 0 or file_index >= len(new_files):
        return redirect('some_error_page')

    current_file = new_files[file_index]

    # Перевіряємо, чи вже існують характеристики для цього файлу
    characteristics = ModelCharacteristics.objects.filter(order_file=current_file).first()

    if request.method == 'POST':
        form = ModelCharacteristicsAddForm(request.POST, instance=characteristics)
        if form.is_valid():
            characteristics = form.save(commit=False)
            characteristics.order_file = current_file
            characteristics.save()

            # Якщо ще є файли, що потребують характеристик, переходимо до наступного
            if file_index + 1 < len(new_files):
                return redirect('order_characteristics_add', order_id=order.id, file_index=file_index + 1)
            else:
                return redirect('order_details_cart', order_id=order.id)
    else:
        form = ModelCharacteristicsAddForm(instance=characteristics)

    return render(request, 'order_html/order_characteristics_add.html', {
        'form': form,
        'file_index': file_index,
        'total_files': len(new_files),
        'file_name': current_file.file_name,
        'order_id': order.id,
    })


@login_required(login_url='/users/login/')
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


@login_required(login_url='/users/login/')
def order_details_cart(request, order_id):
    permission_check = check_order_permissions(request, order_id)
    if permission_check:
        return permission_check  # Якщо немає прав, повертаємо відповідь Forbidden
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_html/order_details_cart.html', {'order': order})


@login_required(login_url='/users/login/')
def user_orders(request):
    query = request.GET.get('q', '').lower().strip()
    orders = (
        OrderInfo.objects
        .select_related('order')
        .filter(user=request.user)
        .annotate(total_copies=Sum('order__files__characteristics__copies'))
        .order_by('-created_at')
    )

    if query:
        # Отримуємо список назв замовлень
        order_titles = list(orders.values_list("order__title", flat=True))

        # Використовуємо fuzzy search для знаходження схожих назв
        matches = process.extract(query, order_titles, limit=10)

        # Витягуємо тільки ті заголовки, що мають схожість >= 50%
        similar_titles = [match[0] for match in matches if match[1] >= 50]

        # Фільтруємо замовлення, які мають схожі назви
        orders = orders.filter(order__title__in=similar_titles)

    return render(request, 'order_html/user_orders.html', {'orders': orders, 'query': query})


@login_required(login_url='/users/login/')
def order_details(request, order_id):
    order_info = get_object_or_404(OrderInfo, id=order_id)
    order = order_info.order  # Отримуємо об'єкт замовлення

    context = {
        'order': order,
        'order_info': order_info,
    }
    return render(request, 'order_html/order_details.html', context)


@login_required(login_url='/users/login/')
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


@login_required(login_url='/users/login/')
def repeat_order(request, order_id):
    # Отримуємо замовлення
    order_info = get_object_or_404(OrderInfo, id=order_id, user=request.user)

    # Перевіряємо, чи замовлення має статус "Розглядається"
    if order_info.status == 'pending':
        return redirect('user_orders')

    # Оновлюємо статус замовлення
    order_info.status = 'pending'  # "Розглядається"
    order_info.order_status = 'created'  # "Оформлено"
    order_info.total_cost = 0  # Встановлюємо вартість на 0

    # Зберігаємо зміни
    order_info.save()

    return redirect('user_orders')  # Перенаправляємо на список замовлень користувача
