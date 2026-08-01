"""Numbers for the admin start page.

Kept to a handful of cheap aggregates so opening the admin stays fast.
"""
from django import template
from django.urls import reverse
from django.utils import timezone

from .. import crm
from ..models import MenuItem, Offer, Reservation

register = template.Library()


@register.simple_tag
def b12_admin_stats():
    """Four counts that tell a manager whether anything needs doing."""
    today = timezone.localdate()

    tonight = Reservation.objects.filter(
        date=today, status__in=crm.COUNTED_STATUSES,
    ).count()
    awaiting = Reservation.objects.filter(status='new', date__gte=today).count()
    customers = crm.build_customers(today)
    lapsed = sum(1 for customer in customers if customer['segment'] == 'lapsed')
    available_items = MenuItem.objects.filter(is_available=True).count()

    reservations_url = reverse('admin:restaurant_reservation_changelist')
    dashboard_url = reverse('restaurant:dashboard')

    return [
        {
            'latin': 'TONIGHT',
            'value': tonight,
            'label': 'حجوزات الليلة',
            'note': f'{today:%d/%m}',
            'url': f'{reservations_url}?date__gte={today.isoformat()}',
            'action': 'اعرض الحجوزات',
        },
        {
            'latin': 'AWAITING',
            'value': awaiting,
            'label': 'تنتظر ردًا',
            'note': 'طلبات جديدة لم يتم التواصل بشأنها' if awaiting else 'لا شيء معلّق',
            'urgent': awaiting > 0,
            'url': f'{reservations_url}?status__exact=new',
            'action': 'راجعها الآن' if awaiting else '',
        },
        {
            'latin': 'CUSTOMERS',
            'value': len(customers),
            'label': 'العملاء',
            'note': f'{lapsed} بحاجة لمتابعة' if lapsed else 'لا أحد انقطع',
            'url': dashboard_url,
            'action': 'لوحة العملاء',
        },
        {
            'latin': 'MENU',
            'value': available_items,
            'label': 'أطباق متاحة',
            'note': f"{Offer.objects.filter(is_active=True).count()} عرضًا فعّالًا",
            'url': reverse('admin:restaurant_menuitem_changelist'),
            'action': 'أدر القائمة',
        },
    ]
