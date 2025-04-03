from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db.models import Case, When, IntegerField, Sum

from admin_panel.forms import MaterialForm, MaterialEditForm, ModeratorForm
from orders.models import Order, OrderInfo, OrderRejection, OrderApproval, ServicePricing, Cart
from posts.models import Post, Comment
from users.models import Notification, User
from fuzzywuzzy import process  # Для fuzzy search


def check_user_role(request):
    # Перевірка ролі користувача
    user_role = request.user.role

    if user_role == 'user':
        # Якщо користувач, перенаправляємо на домашню сторінку
        return redirect('home')
    elif user_role == 'moderator' or user_role == 'admin':
        # Якщо модератор або адміністратор, просто повертаємо None, щоб продовжити виконання
        return None
    else:
        # Якщо роль не визначена, також можна перенаправити
        return redirect('home')


def admin_orders(request):

    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home
    # Пошук
    query = request.GET.get('q', '').lower().strip()

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

    # Пошук
    if query:
        order_titles = list(purchased_orders.values_list("order__title", flat=True))
        matches = process.extract(query, order_titles, limit=10)
        similar_titles = [match[0] for match in matches if match[1] >= 50]  # Фільтрація за схожістю

        # Фільтруємо замовлення за схожими назвами
        purchased_orders = purchased_orders.filter(order__title__in=similar_titles)

    # Сортування
    purchased_orders = purchased_orders.order_by('urgency_priority', 'created_at')

    return render(
        request,
        'admin_panel_html/admin_orders.html',
        {'purchased_orders': purchased_orders, 'query': query},
    )


def admin_order_details(request, order_id):

    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

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
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

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

def delete_material(request, material_id):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    material = get_object_or_404(ServicePricing, id=material_id, parameter_type='material')
    if request.method == 'POST':
        material.delete()
    return redirect('admin_materials')  # Замініть на правильний URL


def edit_material(request, material_id):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    material = get_object_or_404(ServicePricing, id=material_id, parameter_type='material')

    if request.method == 'POST':
        form = MaterialEditForm(request.POST, instance=material)
        if form.is_valid():
            updated_material = form.save(commit=False)
            updated_material.parameter_type = 'material'  # Забезпечуємо, що тип параметра завжди "material"
            updated_material.save()
            return redirect('admin_materials')  # Перенаправлення на список матеріалів після збереження
    else:
        form = MaterialEditForm(instance=material)  # Заповнюємо форму даними існуючого матеріалу

    return render(request, 'admin_panel_html/edit_material.html', {'form': form, 'material': material})


def admin_materials(request):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    materials = ServicePricing.objects.filter(parameter_type='material')
    return render(request, 'admin_panel_html/admin_materials.html', {'materials': materials})


def user_list(request):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    users = User.objects.filter(role='user')  # Отримуємо всіх користувачів зі статусом "Користувач"
    return render(request, 'admin_panel_html/user_list.html', {'users': users})


def admin_user_detail(request, user_id):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    profile_user = get_object_or_404(User, id=user_id)
    notifications = Notification.objects.filter(user=profile_user)
    comments = Comment.objects.filter(author=profile_user)
    posts = Post.objects.filter(author=profile_user)
    orders = Order.objects.filter(user=profile_user)
    cart_items = Cart.objects.filter(user=profile_user)
    order_infos = OrderInfo.objects.filter(user=profile_user)

    context = {
        'profile_user': profile_user,
        'notifications': notifications,
        'comments': comments,
        'posts': posts,
        'orders': orders,
        'cart_items': cart_items,
        'order_infos': order_infos,
    }
    return render(request, 'admin_panel_html/user_admin_detail.html', context)


def moderator_list(request):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    moderators = User.objects.filter(role='moderator')  # Отримуємо всіх модераторів
    return render(request, 'admin_panel_html/moderator_list.html', {'moderators': moderators})


@login_required
def admin_moderator_detail(request, user_id):
    # Перевірка на доступ до функції тільки для адмінів
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    profile_user = get_object_or_404(User, id=user_id, role='moderator')  # Перевірка, що це модератор
    notifications = Notification.objects.filter(user=profile_user)
    comments = Comment.objects.filter(author=profile_user)
    posts = Post.objects.filter(author=profile_user)
    orders = Order.objects.filter(user=profile_user)
    cart_items = Cart.objects.filter(user=profile_user)
    order_infos = OrderInfo.objects.filter(user=profile_user)

    if request.method == 'POST' and 'downgrade' in request.POST:
        # Пониження модератора до користувача
        profile_user.role = 'user'
        profile_user.save()
        return redirect('moderator_list')

    context = {
        'profile_user': profile_user,
        'notifications': notifications,
        'comments': comments,
        'posts': posts,
        'orders': orders,
        'cart_items': cart_items,
        'order_infos': order_infos,
    }
    return render(request, 'admin_panel_html/moderator_admin_detail.html', context)


def admin_list(request):
    redirect_response = check_user_role(request)
    if redirect_response:
        return redirect_response  # Якщо це користувач, перенаправляємо на home

    admins = User.objects.filter(role='admin')  # Отримуємо всіх модераторів

    if request.method == "POST":
        form = ModeratorForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            user.role = 'moderator'
            user.save()
            return redirect('admin_list')  # Перезавантажуємо сторінку

    else:
        form = ModeratorForm()

    return render(request, 'admin_panel_html/admin_list.html', {'admins': admins, 'form': form})


"""
def admin_detail(request, user_id):
    profile_user = get_object_or_404(User, id=user_id, role='admin')  # Перевіряємо, що це модератор
    notifications = Notification.objects.filter(user=profile_user)
    comments = Comment.objects.filter(author=profile_user)
    posts = Post.objects.filter(author=profile_user)
    orders = Order.objects.filter(user=profile_user)
    cart_items = Cart.objects.filter(user=profile_user)
    order_infos = OrderInfo.objects.filter(user=profile_user)

    context = {
        'profile_user': profile_user,
        'notifications': notifications,
        'comments': comments,
        'posts': posts,
        'orders': orders,
        'cart_items': cart_items,
        'order_infos': order_infos,
    }
    return render(request, 'admin_panel_html/admin_detail.html', context) """
