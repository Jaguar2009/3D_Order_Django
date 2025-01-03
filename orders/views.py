from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms import modelform_factory

from .forms import OrderForm, ModelCharacteristicsForm
from .models import Order, OrderFile, ModelCharacteristics, Cart


def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            # Створення замовлення
            order = form.save(commit=False)
            order.user = request.user  # Задати користувача
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

    current_file = files[file_index]

    if request.method == 'POST':
        form = ModelCharacteristicsForm(request.POST)
        if form.is_valid():
            characteristics = form.save(commit=False)
            characteristics.order_file = current_file
            characteristics.save()

            # Перехід до наступного файлу
            if file_index + 1 < files.count():
                return redirect('order_characteristics', order_id=order.id, file_index=file_index + 1)
            else:
                # Після останнього файлу додати замовлення до кошика
                Cart.objects.create(user=request.user, order=order)
                return redirect('cart')

    else:
        form = ModelCharacteristicsForm()

    return render(request, 'order_html/order_characteristics.html', {
        'form': form,
        'file_index': file_index + 1,
        'total_files': files.count(),
        'file_name': current_file.file_name,
        'order_id': order.id,  # Передаємо order_id в шаблон
    })


@login_required
def view_cart(request):
    # Отримуємо всі елементи кошика для поточного користувача
    cart_items = Cart.objects.filter(user=request.user)

    return render(request, 'order_html/cart.html', {'cart_items': cart_items})


@login_required
def remove_from_cart(request, cart_item_id):
    # Видаляємо конкретний товар з кошика
    cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
    cart_item.delete()

    return redirect('cart')

