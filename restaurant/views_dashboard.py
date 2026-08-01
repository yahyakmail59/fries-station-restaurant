"""Staff-only customer dashboard (CRM).

Access reuses the Django admin session, so signing out of the admin signs
out of here too and there is no second set of credentials.
"""
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import crm, panel
from .models import Reservation, RestaurantSettings

# A booking can be moved between these states from the dashboard. Deleting
# a reservation stays in the admin, where it is logged and reversible.
ALLOWED_STATUS_CHANGES = {'new', 'contacted', 'confirmed', 'cancelled'}

# Filters worth carrying across a status change so the list does not reset.
CARRIED_FILTERS = ('q', 'segment', 'sort', 'page')

PER_PAGE = 20


@staff_member_required
def dashboard(request):
    today = timezone.localdate()
    site = RestaurantSettings.load()

    customers = crm.build_customers(today)
    query = request.GET.get('q', '').strip()
    segment = request.GET.get('segment', '')
    sort = request.GET.get('sort', 'last')
    if sort not in crm.SORT_OPTIONS:
        sort = 'last'

    matches = crm.sort_customers(crm.filter_customers(customers, query, segment), sort)
    page = Paginator(matches, PER_PAGE).get_page(request.GET.get('page'))

    # Each summary card carries its own series, so the template stays declarative.
    series = crm.summary_series(customers, today)
    counters = crm.headline(customers, today)
    for counter in counters:
        counter['chart_data'] = series.get(counter.get('chart'))

    return render(request, 'restaurant/dashboard.html', {
        'site': site,
        'today': today,
        'now': timezone.localtime(),
        'counters': counters,
        'segments': crm.segment_counts(customers),
        'awaiting_count': Reservation.objects.filter(status='new', date__gte=today).count(),
        'user_name': request.user.get_full_name() or request.user.get_username(),
        'user_initial': (
            (request.user.get_full_name() or request.user.get_username()).strip()[:1] or '؟'
        ).upper(),
        # Shared sidebar chrome, same as every other panel page.
        'nav_groups': panel.nav(request.user, active='customers'),
        'active_section': 'customers',
        'tonight': crm.tonight(customers, today),
        'page': page,
        'total_customers': len(customers),
        'match_count': len(matches),
        'match_phrase': crm.count_ar(len(matches), 'customer'),
        'query': query,
        'active_segment': segment if segment in crm.SEGMENTS else '',
        'sort': sort,
        'sort_options': [
            {'value': value, 'label': label} for value, label in crm.SORT_OPTIONS.items()
        ],
        'is_filtered': bool(query or segment),
        'carried_query': _carried_query(request),
        'can_edit_reservations': request.user.has_perm('restaurant.change_reservation'),
        'reservations_url': reverse('admin:restaurant_reservation_changelist'),
    })


@staff_member_required
@require_POST
def update_reservation_status(request, pk):
    if not request.user.has_perm('restaurant.change_reservation'):
        raise PermissionDenied

    status = request.POST.get('status', '')
    if status not in ALLOWED_STATUS_CHANGES:
        messages.error(request, 'حالة الحجز غير معروفة.')
        return redirect(_return_url(request))

    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status != status:
        reservation.status = status
        reservation.save(update_fields=['status', 'updated_at'])
        label = dict(Reservation.STATUS_CHOICES)[status]
        messages.success(request, f'حجز {reservation.full_name}: {label}.')

    return redirect(_return_url(request))


def _carried_query(request):
    """The current filters, ready to embed in a form that must preserve them."""
    return {key: request.GET.get(key, '') for key in CARRIED_FILTERS if request.GET.get(key)}


def _return_url(request):
    """Come back to the same filtered list the action was taken from."""
    base = reverse('restaurant:dashboard')
    params = {key: request.POST.get(key, '') for key in CARRIED_FILTERS if request.POST.get(key)}
    url = f'{base}?{urlencode(params)}' if params else base
    return f'{url}#tonight'
