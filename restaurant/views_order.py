"""Server-side ordering.

The browser posts dish ids and quantities. It does not post prices, and any
price it does post is ignored. Everything the restaurant is owed is read
from the menu here, which is the whole point: the WhatsApp message stops
being the source of truth and becomes a pointer to this record.
"""
import json
import logging
from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .models import MenuItem, Offer, Order, OrderLine, RestaurantSettings
from .receipt import render_order
from .views import _client_address

logger = logging.getLogger(__name__)

MAX_LINES = 40
MAX_QUANTITY = 99
ORDER_RATE_LIMIT = 12
ORDER_RATE_WINDOW = 600


def _rate_limited(request):
    key = f'order-rate:{_client_address(request)}'
    if cache.add(key, 1, timeout=ORDER_RATE_WINDOW):
        return False
    try:
        return cache.incr(key) > ORDER_RATE_LIMIT
    except ValueError:
        cache.set(key, 1, timeout=ORDER_RATE_WINDOW)
        return False


def _error(language, arabic, english, status=400):
    """A refusal the customer can read.

    This endpoint answers JSON, so its errors never pass through a template
    and are shown to the customer exactly as written here. Every one of them
    therefore has to follow the language the visitor chose, the same as the
    reservation form and the cart already do.
    """
    return JsonResponse({'error': arabic if language == 'ar' else english}, status=status)


def _resolve_price(item, size_id):
    """The price the restaurant is owed for one unit, and what to call it.

    The browser sends a size id, never a price. If the dish has sizes and the
    id does not match one of its own available rows, this falls back to the
    cheapest size rather than refusing: the cheapest is what the card
    advertised, so a stale or tampered id can never charge more than the
    customer was shown.
    """
    sizes = item.available_sizes
    if not sizes:
        return item.price, '', ''
    chosen = next((size for size in sizes if size.pk == size_id), sizes[0])
    return chosen.price, chosen.name_ar, chosen.name_en


def _clean_text(value, limit):
    return str(value or '').strip()[:limit]


def _phone_digits(value):
    return ''.join(character for character in str(value or '') if character.isdigit())


@require_POST
def create_order(request):
    language = request.session.get('site_language', 'ar')
    if _rate_limited(request):
        return _error(
            language,
            'محاولات كثيرة. انتظر قليلًا ثم أعد المحاولة.',
            'Too many attempts. Please wait and try again.',
            status=429,
        )

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return _error(language, 'طلب غير صالح.', 'Invalid request.')

    raw_items = payload.get('items')
    if not isinstance(raw_items, list) or not raw_items:
        return _error(language, 'السلة فارغة.', 'Your cart is empty.')
    if len(raw_items) > MAX_LINES:
        return _error(language, 'عدد الأصناف كبير جدًا.', 'That is too many items for one order.')

    # Only ids, sizes and quantities are read. A price in the payload is
    # ignored, and so is any size that does not belong to the dish it was sent
    # with — the size is a pointer to a row, never a number.
    wanted_items, wanted_offers = {}, {}
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        try:
            quantity = int(entry.get('qty', 0))
        except (TypeError, ValueError):
            continue
        if not 1 <= quantity <= MAX_QUANTITY:
            continue

        raw_id = str(entry.get('id', ''))
        if raw_id.startswith('offer-'):
            key = raw_id.removeprefix('offer-')
            if not key.isdigit():
                continue
            wanted_offers[int(key)] = wanted_offers.get(int(key), 0) + quantity
            continue

        if not raw_id.isdigit():
            continue
        raw_size = str(entry.get('size', ''))
        size_id = int(raw_size) if raw_size.isdigit() else None
        # One line per dish-and-size pair: a small and a large of the same
        # dish are two different things to make and to charge for.
        line_key = (int(raw_id), size_id)
        wanted_items[line_key] = wanted_items.get(line_key, 0) + quantity

    if not wanted_items and not wanted_offers:
        return _error(language, 'لا يوجد صنف صالح في السلة.', 'No valid item was found in your cart.')

    site = RestaurantSettings.load()
    fulfillment = 'delivery' if payload.get('fulfillment') == 'delivery' else 'pickup'
    name = _clean_text(payload.get('name'), 150)
    phone = _clean_text(payload.get('phone'), 40)
    address = _clean_text(payload.get('address'), 500)
    notes = _clean_text(payload.get('notes'), 500)

    if fulfillment == 'delivery':
        digits = _phone_digits(phone)
        if not name or not address or not 7 <= len(digits) <= 15:
            return _error(
                language,
                'أدخل الاسم ورقم جوال صحيح وعنوان التوصيل.',
                'Enter a name, a valid phone number and a delivery address.',
            )

    with transaction.atomic():
        order = Order.objects.create(
            fulfillment=fulfillment,
            customer_name=name,
            phone=phone,
            address=address if fulfillment == 'delivery' else '',
            notes=notes,
            currency=site.currency,
            restaurant_name=site.name_ar,
            restaurant_tagline=site.tagline_ar,
            language=language,
        )

        total = Decimal('0')
        has_unpriced = False
        lines = []

        item_ids = {item_id for item_id, _ in wanted_items}
        available = {
            item.pk: item
            for item in MenuItem.objects.filter(
                pk__in=item_ids, is_available=True
            ).prefetch_related('sizes')
        }
        for (item_id, size_id), quantity in wanted_items.items():
            item = available.get(item_id)
            if item is None:
                continue
            unit_price, label_ar, label_en = _resolve_price(item, size_id)
            total += unit_price * quantity
            lines.append(OrderLine(
                order=order, menu_item=item,
                name_ar=item.name_ar, name_en=item.name_en,
                size_label_ar=label_ar, size_label_en=label_en,
                quantity=quantity, unit_price=unit_price, is_priced=True,
            ))

        for offer in Offer.objects.filter(pk__in=wanted_offers, is_active=True):
            quantity = wanted_offers[offer.pk]
            # Offer prices are free text ("عائلي 99 ₪"), so they are quoted,
            # not computed. The restaurant confirms them by hand.
            has_unpriced = True
            lines.append(OrderLine(
                order=order, offer=offer,
                name_ar=offer.title_ar, name_en=offer.title_en,
                quantity=quantity, unit_price=Decimal('0'), is_priced=False,
                price_note=offer.price_text_ar or '',
            ))

        if not lines:
            transaction.set_rollback(True)
            return _error(
                language,
                'الأصناف المطلوبة لم تعد متاحة.',
                'The items you asked for are no longer available.',
                status=409,
            )

        OrderLine.objects.bulk_create(lines)
        order.total = total
        order.has_unpriced_lines = has_unpriced
        order.save(update_fields=['total', 'has_unpriced_lines', 'updated_at'])

    order_url = request.build_absolute_uri(reverse('restaurant:order_detail', args=[order.token]))
    number = ''.join(character for character in site.whatsapp_number if character.isdigit())
    message = _whatsapp_message(order, order_url, language)

    return JsonResponse({
        'code': order.code,
        'order_url': order_url,
        'receipt_url': request.build_absolute_uri(
            reverse('restaurant:order_receipt', args=[order.token])
        ),
        'whatsapp_url': f'https://wa.me/{number}?text={quote(message)}' if number else '',
        'message': message,
    })


def _whatsapp_message(order, order_url, language):
    """Short on purpose: the order page carries the detail, this carries the key.

    The link gets a line to itself, with nothing before it — not even an
    invisible direction mark. WhatsApp only linkifies a run that starts at
    'http', so a leading character stops it becoming tappable, and anyone
    copying the text would carry that character into the address bar. A line
    holding only a URL already reads left-to-right without help.
    """
    if language == 'en':
        return '\n'.join([
            'Hello B12, I placed an order on the website.',
            f'Order number: {order.code}',
            'View order:',
            order_url,
        ])
    return '\n'.join([
        'السلام عليكم، أرسلت طلبًا من الموقع',
        f'رقم الطلب: {order.code}',
        'عرض الطلب:',
        order_url,
    ])


@require_GET
def order_receipt(request, token):
    """The PNG the customer shares into WhatsApp."""
    order = get_object_or_404(Order.objects.prefetch_related('lines'), token=token)
    try:
        png = render_order(order)
    except Exception:
        logger.exception('Failed to render receipt for order %s', order.code)
        raise Http404('تعذر إنشاء صورة الفاتورة.')

    response = HttpResponse(png, content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="{order.code}.png"'
    response['Cache-Control'] = 'private, max-age=600'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@require_GET
def order_detail(request, token):
    """Opened from the WhatsApp link. Read-only; staff act from the panel."""
    order = get_object_or_404(Order.objects.prefetch_related('lines'), token=token)
    return render(request, 'restaurant/order_detail.html', {
        'order': order,
        'site': RestaurantSettings.load(),
        'receipt_url': reverse('restaurant:order_receipt', args=[order.token]),
        'is_staff_viewer': request.user.is_authenticated and request.user.is_staff,
        'can_manage_order': request.user.has_perm('restaurant.change_order'),
    })
