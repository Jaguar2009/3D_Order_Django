from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db.models import Case, When, IntegerField, Sum

from admin_panel.forms import MaterialForm
from orders.models import Order, OrderInfo, OrderRejection, OrderApproval, ServicePricing
from users.models import Notification


def admin_orders(request):

    # Фільтри
    status_filter = request.GET.get('status', 'pending')  # За замовчуванням 'pending'
    urgency_filter = request.GET.get('urgency', 'all')  # За замовчуванням 'all'
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)

    purchased_orders = (
        OrderInfo.objects
        .select_related('order', 'user')
        .filter(status=status_filter)  # Фільтр по статусу
        .annotate(
            urgency_priority=Case(
                When(order__delivery_time='Urgent', then=1),
                When(order__delivery_time='By Agreement', then=2),
                When(order__delivery_time='Standard', then=3),
                default=4,
                output_field=IntegerField(),
            ),
            total_copies=Sum('order__files__characteristics__copies'),
        )
    )

    # Фільтрування по терміновості
    if urgency_filter != 'all':
        purchased_orders = purchased_orders.filter(order__delivery_time=urgency_filter)

    # Фільтрування по датах
    if date_from:
        purchased_orders = purchased_orders.filter(created_at__gte=date_from)
    if date_to:
        purchased_orders = purchased_orders.filter(created_at__lte=date_to)

    # Сортування
    purchased_orders = purchased_orders.order_by('urgency_priority', 'created_at')

    return render(
        request,
        'admin_panel_html/admin_orders.html',
        {'purchased_orders': purchased_orders},
    )


def admin_order_details(request, order_id):

    order = get_object_or_404(Order, id=order_id)
    order_infos = OrderInfo.objects.filter(order=order)
    files = order.files.prefetch_related('characteristics')

    if request.method == 'POST':
        purchased_order_id = request.POST.get('order_info_id')
        purchased_order = get_object_or_404(OrderInfo, id=purchased_order_id)

        # Обробка підтвердження
        if 'confirm' in request.POST:
            # Отримуємо витрати пластика для кожного файлу
            plastic_usage_per_file = {}
            for file in purchased_order.order.files.all():
                usage_key = f'plastic_usage_{file.id}'
                plastic_usage = request.POST.get(usage_key, 0)
                plastic_usage_per_file[file.id] = float(plastic_usage)

            # Створюємо або оновлюємо OrderApproval
            approval, created = OrderApproval.objects.get_or_create(order_info=purchased_order)
            approval.plastic_usage_per_file = plastic_usage_per_file
            approval.save()

            # Розрахунок загальних витрат матеріалу та вартості
            total_plastic_usage = approval.calculate_plastic_usage()
            purchased_order.status = 'approved'
            purchased_order.save()

            # Розрахунок загальної вартості
            purchased_order.total_cost = purchased_order.calculate_total_cost()
            purchased_order.save()

            # Створення повідомлення про підтвердження замовлення
            Notification.objects.create(
                user=purchased_order.user,
                title="Ваше замовлення підтверджено",
                text=f"До сплати: {purchased_order.total_cost} грн.",
            )

            return redirect('admin_orders')

        # Обробка відхилення
        elif 'reject' in request.POST:
            rejection_reason = request.POST.get('rejection_reason', '').strip()  # Отримуємо причину відмови
            if rejection_reason:
                # Видаляємо існуюче відхилення, якщо воно є
                OrderRejection.objects.filter(order_info=purchased_order).delete()

                # Створюємо нове відхилення
                OrderRejection.objects.create(
                    order_info=purchased_order, rejection_reason=rejection_reason
                )
                purchased_order.status = 'rejected'
                purchased_order.save()

                # Створення повідомлення про відхилення замовлення
                Notification.objects.create(
                    user=purchased_order.user,
                    title="Ваше замовлення відхилено",
                    text=f"Причина відмови: {rejection_reason}",
                )

            return redirect('admin_orders')

    return render(
        request,
        'admin_panel_html/admin_order_details.html',
        {
            'order': order,
            'files': files,
            'order_infos': order_infos,
        },
    )

def create_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.parameter_type = 'material'  # Фіксований тип
            material.save()
            return redirect('admin_materials')  # Змінити на вашу сторінку зі списком матеріалів
    else:
        form = MaterialForm()

    return render(request, 'admin_panel_html/create_material.html', {'form': form})

def admin_materials(request):
    materials = ServicePricing.objects.filter(parameter_type='material')
    return render(request, 'admin_panel_html/admin_materials.html', {'materials': materials})



