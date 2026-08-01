from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from . import panel
from .models import MenuItem, Order, OrderLine, RestaurantSettings

MAX_LINES = 40
MAX_QUANTITY = 99


def _clean(value, limit):
    return str(value or '').strip()[:limit]


def _today_stats():
    today = timezone.localdate()
    orders = Order.objects.filter(created_at__date=today).exclude(status='cancelled')
    inside = orders.filter(source='cashier').aggregate(
        value=Coalesce(Sum('customer_count'), 0)
    )['value']
    outside = orders.filter(source='online').aggregate(
        value=Coalesce(Sum('customer_count'), 0)
    )['value']
    sales = orders.aggregate(value=Coalesce(Sum('total'), Decimal('0')))['value']
    return {
        'inside_customers': inside,
        'outside_customers': outside,
        'orders_count': orders.count(),
        'sales': sales,
    }


def _context(request, *, selected=None, values=None):
    site = RestaurantSettings.load()
    selected = selected or {}
    items = list(
        MenuItem.objects.filter(is_available=True).select_related(
            'category'
        ).order_by('category__display_order', 'category__id', 'display_order', 'id')
    )
    for item in items:
        item.selected_quantity = selected.get(item.pk, 0)

    created_order = None
    created_token = request.GET.get('created', '')
    if created_token:
        created_order = Order.objects.filter(
            token=created_token,
            source='cashier',
        ).prefetch_related('lines').first()

    return {
        'site': site,
        'nav_groups': panel.nav(request.user),
        'active_section': 'cashier',
        'user_name': request.user.get_full_name() or request.user.get_username(),
        'user_initial': (
            (request.user.get_full_name() or request.user.get_username()).strip()[:1] or 'ك'
        ).upper(),
        'items': items,
        'values': values or {},
        'stats': _today_stats(),
        'created_order': created_order,
        'recent_orders': Order.objects.filter(source='cashier').select_related(
            'cashier'
        ).prefetch_related('lines')[:8],
    }


@staff_member_required
def cashier(request):
    if not request.user.has_perm('restaurant.add_order'):
        raise PermissionDenied

    if request.method != 'POST':
        return render(request, 'restaurant/cashier.html', _context(request))

    available_items = list(
        MenuItem.objects.filter(is_available=True).select_related('category')
    )
    selected = {}
    invalid_quantity = False
    for item in available_items:
        raw_quantity = request.POST.get(f'quantity_{item.pk}', '0')
        try:
            quantity = int(raw_quantity or 0)
        except (TypeError, ValueError):
            invalid_quantity = True
            continue
        if quantity < 0 or quantity > MAX_QUANTITY:
            invalid_quantity = True
            continue
        if quantity:
            selected[item.pk] = quantity

    values = {
        'customer_name': _clean(request.POST.get('customer_name'), 150),
        'customer_count': _clean(request.POST.get('customer_count'), 3),
        'table_number': _clean(request.POST.get('table_number'), 30),
        'notes': _clean(request.POST.get('notes'), 500),
    }

    try:
        customer_count = int(values['customer_count'])
    except (TypeError, ValueError):
        customer_count = 0

    if not 1 <= customer_count <= 100:
        messages.error(request, 'أدخل عدد زبائن صحيحًا بين 1 و100.')
    elif invalid_quantity:
        messages.error(request, 'راجع كميات الأصناف؛ الحد الأقصى للصنف 99.')
    elif not selected:
        messages.error(request, 'اختر صنفًا واحدًا على الأقل قبل حفظ الطلب.')
    elif len(selected) > MAX_LINES:
        messages.error(request, 'عدد الأصناف في الطلب أكبر من الحد المسموح.')
    else:
        site = RestaurantSettings.load()
        with transaction.atomic():
            order = Order.objects.create(
                source='cashier',
                fulfillment='dine_in',
                status='confirmed',
                customer_name=values['customer_name'],
                customer_count=customer_count,
                table_number=values['table_number'],
                notes=values['notes'],
                cashier=request.user,
                currency=site.currency,
                restaurant_name=site.name_ar,
                restaurant_tagline=site.tagline_ar,
                language='ar',
            )
            total = Decimal('0')
            lines = []
            for item in available_items:
                quantity = selected.get(item.pk)
                if not quantity:
                    continue
                total += item.price * quantity
                lines.append(OrderLine(
                    order=order,
                    menu_item=item,
                    name_ar=item.name_ar,
                    name_en=item.name_en,
                    quantity=quantity,
                    unit_price=item.price,
                    is_priced=True,
                ))
            OrderLine.objects.bulk_create(lines)
            order.total = total
            order.save(update_fields=['total', 'updated_at'])

        messages.success(request, f'تم حفظ طلب الكاشير {order.code} بنجاح.')
        return redirect(
            f"{reverse('restaurant:cashier')}?created={order.token}"
        )

    return render(
        request,
        'restaurant/cashier.html',
        _context(request, selected=selected, values=values),
        status=400,
    )
