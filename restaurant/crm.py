"""Customer records derived from reservations.

The restaurant already knows its customers — every reservation carries a
name, a phone number and a party size. This module groups that history by
phone number (the one stable identifier a guest gives) so staff can see who
comes back, who is worth a thank-you, and who has quietly stopped coming.

No customer table is stored: the records are always read from reservations,
so nothing can drift out of sync with the booking history.
"""
from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from .models import Reservation

# A cancelled booking is not a visit, and never counts towards loyalty.
COUNTED_STATUSES = ('new', 'contacted', 'confirmed')

# A regular who has not been seen in this long is worth a phone call.
LAPSED_AFTER_DAYS = 60
VIP_VISITS = 5
RHYTHM_MONTHS = 12

SEGMENTS = {
    'lapsed': {'label': 'انقطع', 'tone': 'lapsed', 'hint': 'كان يزور بانتظام وغاب'},
    'vip': {'label': 'عميل دائم', 'tone': 'vip', 'hint': '٥ زيارات فأكثر'},
    'regular': {'label': 'متكرر', 'tone': 'regular', 'hint': 'من زيارتين إلى أربع'},
    'new': {'label': 'جديد', 'tone': 'new', 'hint': 'زيارة واحدة حتى الآن'},
}

SEGMENT_ORDER = ['lapsed', 'vip', 'regular', 'new']

SORT_OPTIONS = {
    'last': 'آخر زيارة',
    'visits': 'عدد الزيارات',
    'covers': 'عدد الضيوف',
    'name': 'الاسم',
}

# Arabic counts agree with the number: 2 takes the dual, 3–10 the plural,
# and 11+ the accusative singular. (singular, dual, plural, accusative)
NOUNS = {
    'visit': ('زيارة واحدة', 'زيارتان', 'زيارات', 'زيارة'),
    'customer': ('عميل واحد', 'عميلان', 'عملاء', 'عميلًا'),
    'guest': ('ضيف واحد', 'ضيفان', 'ضيوف', 'ضيفًا'),
    'booking': ('حجز واحد', 'حجزان', 'حجوزات', 'حجزًا'),
    'day': ('يوم واحد', 'يومان', 'أيام', 'يومًا'),
    'month': ('شهر واحد', 'شهران', 'أشهر', 'شهرًا'),
}


def count_ar(value, noun):
    """Render a count the way Arabic actually reads it, not '4 زيارة'."""
    singular, dual, plural, accusative = NOUNS[noun]
    if value == 1:
        return singular
    if value == 2:
        return dual
    if 3 <= value <= 10:
        return f'{value} {plural}'
    return f'{value} {accusative}'


def phone_key(value):
    """Digits only, so 059-786-2389 and 0597862389 are the same person."""
    return ''.join(character for character in value if character.isdigit())


def _relative_day_phrase(days):
    if days == 0:
        return 'اليوم'
    if days == 1:
        return 'أمس'
    # The dual takes the genitive after a preposition: قبل يومين, not قبل يومان.
    if days == 2:
        return 'قبل يومين'
    if days < 30:
        return f"قبل {count_ar(days, 'day')}"
    months = days // 30
    if months == 2:
        return 'قبل شهرين'
    return f"قبل {count_ar(months, 'month')}"


def _month_key(value):
    return value.year * 12 + value.month


def _visit_rhythm(months_visited, today):
    """Twelve cells, newest last — visits per month at a glance."""
    current = _month_key(today)
    cells = []
    for offset in range(RHYTHM_MONTHS - 1, -1, -1):
        key = current - offset
        visits = months_visited.get(key, 0)
        if visits == 0:
            level = 0
        elif visits == 1:
            level = 1
        elif visits <= 3:
            level = 2
        else:
            level = 3
        year, month = divmod(key - 1, 12)
        cells.append({
            'level': level,
            'visits': visits,
            'label': f'{month + 1:02d}/{year % 100:02d}',
        })
    return cells


def _segment_for(visits, days_since_last):
    if visits >= 2 and days_since_last is not None and days_since_last > LAPSED_AFTER_DAYS:
        return 'lapsed'
    if visits >= VIP_VISITS:
        return 'vip'
    if visits >= 2:
        return 'regular'
    return 'new'


def build_customers(today=None):
    """One record per phone number, newest activity first."""
    today = today or timezone.localdate()
    rows = Reservation.objects.values_list(
        'phone', 'full_name', 'date', 'guests', 'status', 'occasion',
    ).order_by('date')

    grouped = defaultdict(lambda: {
        'visits': 0,
        'visits_today': 0,
        'covers': 0,
        'upcoming': 0,
        'cancellations': 0,
        'first_visit': None,
        'last_visit': None,
        'next_visit': None,
        'name': '',
        'phone': '',
        'occasions': [],
        'months': defaultdict(int),
    })

    for phone, name, day, guests, status, occasion in rows:
        key = phone_key(phone)
        if not key:
            continue
        record = grouped[key]
        record['phone'] = phone
        if name:
            record['name'] = name  # rows are date-ordered, so the newest name wins

        if status == 'cancelled':
            record['cancellations'] += 1
            continue

        if day > today:
            record['upcoming'] += 1
            if record['next_visit'] is None or day < record['next_visit']:
                record['next_visit'] = day
            continue

        record['visits'] += 1
        if day == today:
            record['visits_today'] += 1
        record['covers'] += guests
        record['months'][_month_key(day)] += 1
        if record['first_visit'] is None or day < record['first_visit']:
            record['first_visit'] = day
        if record['last_visit'] is None or day > record['last_visit']:
            record['last_visit'] = day
        if occasion:
            record['occasions'].append(occasion)

    customers = []
    for key, record in grouped.items():
        days_since_last = (today - record['last_visit']).days if record['last_visit'] else None
        segment = _segment_for(record['visits'], days_since_last)
        meta = SEGMENTS[segment]
        customers.append({
            'key': key,
            'name': record['name'] or 'بدون اسم',
            'initial': (record['name'].strip()[:1] or '؟').upper(),
            'phone': record['phone'],
            'whatsapp_url': f'https://wa.me/{key}',
            'call_url': f'tel:{key}',
            'visits': record['visits'],
            'prior_visits': record['visits'] - record['visits_today'],
            'covers': record['covers'],
            'upcoming': record['upcoming'],
            'cancellations': record['cancellations'],
            'first_visit': record['first_visit'],
            'last_visit': record['last_visit'],
            'next_visit': record['next_visit'],
            'days_since_last': days_since_last,
            'last_visit_phrase': (
                _relative_day_phrase(days_since_last) if days_since_last is not None else 'لم يزر بعد'
            ),
            'visits_phrase': count_ar(record['visits'], 'visit'),
            'covers_phrase': count_ar(record['covers'], 'guest'),
            'segment': segment,
            'segment_label': meta['label'],
            'segment_tone': meta['tone'],
            'favourite_occasion': (
                max(set(record['occasions']), key=record['occasions'].count)
                if record['occasions'] else ''
            ),
            'rhythm': _visit_rhythm(record['months'], today),
            'months': dict(record['months']),
        })

    return customers


# Sparkline windows for the summary cards.
CHART_MONTHS = 9
CHART_WEEKS = 9


def _bars(values):
    """Heights as percentages of the tallest bar."""
    peak = max(values) if values else 0
    return [
        {'value': value, 'height': round(value / peak * 100) if peak else 0}
        for value in values
    ]


def _line_points(values, width=100, height=34):
    """An SVG polyline for a series, drawn on a fixed viewBox."""
    if not values:
        return ''
    peak = max(values)
    floor = min(values)
    span = (peak - floor) or 1
    step = width / (len(values) - 1) if len(values) > 1 else width
    points = []
    for index, value in enumerate(values):
        x = round(index * step, 2)
        y = round(height - ((value - floor) / span) * (height - 4) - 2, 2)
        points.append(f'{x},{y}')
    return ' '.join(points)


def summary_series(customers, today=None):
    """Real series behind the summary cards — no smoothing, no projection."""
    today = today or timezone.localdate()
    current = _month_key(today)
    months = [current - offset for offset in range(CHART_MONTHS - 1, -1, -1)]

    known_by_month = []
    return_rate_by_month = []
    for key in months:
        known = 0
        returning = 0
        for customer in customers:
            first = customer['first_visit']
            if first and _month_key(first) <= key:
                known += 1
                visits = sum(
                    count for month, count in customer['months'].items() if month <= key
                )
                if visits >= 2:
                    returning += 1
        known_by_month.append(known)
        return_rate_by_month.append(round(returning / known * 100) if known else 0)

    new_by_week = []
    for offset in range(CHART_WEEKS - 1, -1, -1):
        end = today - timedelta(days=7 * offset)
        start = end - timedelta(days=6)
        new_by_week.append(sum(
            1 for customer in customers
            if customer['first_visit'] and start <= customer['first_visit'] <= end
        ))

    return {
        'total': {'kind': 'line', 'points': _line_points(known_by_month), 'values': known_by_month},
        'new': {'kind': 'bars', 'bars': _bars(new_by_week)},
        'returning': {'kind': 'line', 'points': _line_points(return_rate_by_month), 'values': return_rate_by_month},
    }


def filter_customers(customers, query='', segment=''):
    """Search matches a name or any part of the phone number."""
    result = customers
    if segment in SEGMENTS:
        result = [item for item in result if item['segment'] == segment]

    needle = query.strip()
    if needle:
        digits = phone_key(needle)
        lowered = needle.lower()
        result = [
            item for item in result
            if lowered in item['name'].lower() or (digits and digits in item['key'])
        ]
    return result


def sort_customers(customers, sort='last'):
    if sort == 'visits':
        return sorted(customers, key=lambda item: (-item['visits'], -item['covers']))
    if sort == 'covers':
        return sorted(customers, key=lambda item: -item['covers'])
    if sort == 'name':
        return sorted(customers, key=lambda item: item['name'])
    # Newest activity first; customers with no visit yet fall to the end.
    return sorted(
        customers,
        key=lambda item: (item['last_visit'] is None, -(item['last_visit'].toordinal() if item['last_visit'] else 0)),
    )


def segment_counts(customers):
    counts = {key: 0 for key in SEGMENTS}
    for customer in customers:
        counts[customer['segment']] += 1
    return [
        {
            'key': key,
            'label': SEGMENTS[key]['label'],
            'hint': SEGMENTS[key]['hint'],
            'tone': SEGMENTS[key]['tone'],
            'count': counts[key],
        }
        for key in SEGMENT_ORDER
    ]


def headline(customers, today=None):
    """Four numbers a restaurant owner can act on."""
    today = today or timezone.localdate()
    total = len(customers)
    returning = sum(1 for item in customers if item['visits'] >= 2)
    new_this_month = sum(
        1 for item in customers
        if item['first_visit'] and (today - item['first_visit']).days < 30
    )
    lapsed = sum(1 for item in customers if item['segment'] == 'lapsed')

    return [
        {
            'key': 'total',
            'chart': 'total',
            'value': total,
            'label': 'إجمالي العملاء',
            'latin': 'CUSTOMERS',
            'note': f"{count_ar(returning, 'customer')} عادوا أكثر من مرة" if total else 'لا عملاء بعد',
        },
        {
            'key': 'new',
            'chart': 'new',
            'value': new_this_month,
            'label': 'عملاء جدد',
            'latin': 'NEW IN 30 DAYS',
            'note': 'أول زيارة خلال الشهر الماضي',
        },
        {
            'key': 'returning',
            'chart': 'returning',
            'value': round(returning / total * 100) if total else 0,
            'suffix': '٪',
            'label': 'نسبة العودة',
            'latin': 'RETURN RATE',
            'note': 'من العملاء زاروا أكثر من مرة',
        },
        {
            'key': 'lapsed',
            'value': lapsed,
            'label': 'بحاجة لمتابعة',
            'latin': 'WIN BACK',
            'note': f'لم يزوروا منذ أكثر من {LAPSED_AFTER_DAYS} يومًا' if lapsed else 'لا أحد انقطع',
            'urgent': lapsed > 0,
        },
    ]


def tonight(customers, today=None):
    """Tonight's bookings, each tagged with how well the guest is known."""
    today = today or timezone.localdate()
    by_key = {item['key']: item for item in customers}
    bookings = (
        Reservation.objects.filter(date=today, status__in=COUNTED_STATUSES)
        .order_by('time')
    )

    rows = []
    for booking in bookings:
        customer = by_key.get(phone_key(booking.phone))
        # Visits before today, so tonight reads as the next one up.
        previous = customer['prior_visits'] if customer else 0
        rows.append({
            'object': booking,
            'initial': (booking.full_name.strip()[:1] or '؟').upper(),
            'guests_phrase': count_ar(booking.guests, 'guest'),
            'whatsapp_url': f'https://wa.me/{phone_key(booking.phone)}' if phone_key(booking.phone) else '',
            'is_first_visit': previous == 0,
            'visit_badge': 'أول زيارة' if previous == 0 else f'الزيارة رقم {previous + 1}',
            'segment_tone': customer['segment_tone'] if customer else 'new',
            'is_regular': previous >= 2,
            'status': booking.status,
        })
    return rows
