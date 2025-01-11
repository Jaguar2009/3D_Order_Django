from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, IntegerField, Sum
from orders.models import PurchasedOrder, Order


def admin_orders(request):
    if not request.user.is_staff:
        return redirect('home')

    purchased_orders = (
        PurchasedOrder.objects.select_related('order', 'user')
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
        .order_by('urgency_priority', 'created_at')
    )

    return render(
        request,
        'admin_panel_html/admin_orders.html',
        {'purchased_orders': purchased_orders},
    )

def admin_order_details(request, order_id):
    if not request.user.is_staff:
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    files = order.files.prefetch_related('characteristics')

    return render(
        request,
        'admin_panel_html/admin_order_details.html',
        {'order': order, 'files': files},
    )