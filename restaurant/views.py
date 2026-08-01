import logging
from urllib.parse import quote
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import ReservationForm
from .models import Category, FAQ, HeroStat, MenuItem, Offer, Reservation, RestaurantSettings, Service, SocialPost, Testimonial

logger = logging.getLogger(__name__)


def _language(request):
    requested = request.GET.get('lang')
    if requested in {'ar', 'en'}:
        request.session['site_language'] = requested
    return request.session.get('site_language', 'ar')


def _absolute_media_url(request, value):
    if not value:
        return ''
    if urlsplit(value).scheme in {'http', 'https'}:
        return value
    return request.build_absolute_uri(value)


def _best_sellers(available_items):
    counted_orders = ~Q(order_lines__order__status='cancelled')
    return available_items.annotate(
        order_count=Sum(
            'order_lines__quantity',
            filter=counted_orders,
            default=0,
        ),
        online_order_count=Sum(
            'order_lines__quantity',
            filter=counted_orders & Q(order_lines__order__source='online'),
            default=0,
        ),
        cashier_order_count=Sum(
            'order_lines__quantity',
            filter=counted_orders & Q(order_lines__order__source='cashier'),
            default=0,
        ),
    ).filter(order_count__gt=0).order_by('-order_count', 'display_order', 'id')[:4]


def _home_context(request, reservation_form=None, language=None):
    language = language or _language(request)
    settings_obj = RestaurantSettings.load()
    available_items = MenuItem.objects.filter(is_available=True).select_related('category')

    return {
        'language': language,
        'site': settings_obj,
        'home_abs_url': request.build_absolute_uri(reverse('restaurant:home')),
        'og_image_url': _absolute_media_url(request, settings_obj.og_image_src),
        'hero_stats': HeroStat.objects.filter(is_active=True),
        'categories': Category.objects.filter(is_active=True),
        'menu_items': available_items.order_by('-is_featured', 'display_order', 'id'),
        'best_sellers': _best_sellers(available_items),
        'offers': Offer.objects.filter(is_active=True),
        'services': Service.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'faqs': FAQ.objects.filter(is_active=True),
        'social_posts': SocialPost.objects.filter(is_active=True).exclude(
            image='', image_url__contains='/demo/'
        ).order_by('display_order', '-id'),
        'reservation_form': reservation_form or ReservationForm(language=language, site=settings_obj),
    }


def home(request):
    language = _language(request)
    draft = request.session.pop('reservation_draft', None)
    settings_obj = RestaurantSettings.load()
    reservation_form = ReservationForm(draft, language=language, site=settings_obj) if draft else None
    return render(
        request,
        'restaurant/home.html',
        _home_context(request, reservation_form=reservation_form, language=language),
    )


def menu_page(request):
    language = _language(request)
    site = RestaurantSettings.load()
    categories = Category.objects.filter(is_active=True)
    available_items = MenuItem.objects.filter(
        is_available=True,
        category__is_active=True,
    ).select_related('category')
    requested_category = request.GET.get('category', '')
    active_category = (
        requested_category
        if requested_category and categories.filter(slug=requested_category).exists()
        else 'all'
    )
    page_abs_url = request.build_absolute_uri(reverse('restaurant:menu'))

    return render(request, 'restaurant/menu.html', {
        'language': language,
        'site': site,
        'is_menu_page': True,
        'page_abs_url': page_abs_url,
        'home_abs_url': request.build_absolute_uri(reverse('restaurant:home')),
        'og_image_url': _absolute_media_url(request, site.og_image_src),
        'categories': categories,
        'menu_items': available_items.order_by('category__display_order', 'display_order', 'id'),
        'best_sellers': _best_sellers(available_items),
        'offers': Offer.objects.filter(is_active=True) if site.show_offers else Offer.objects.none(),
        'active_category': active_category,
    })


def _client_address(request):
    address = request.META.get('REMOTE_ADDR', 'unknown')
    trusted_hops = max(0, getattr(settings, 'TRUSTED_PROXY_HOPS', 0))
    if trusted_hops:
        forwarded = [
            value.strip()
            for value in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')
            if value.strip()
        ]
        if len(forwarded) >= trusted_hops:
            address = forwarded[-trusted_hops]
    return address


def _reservation_rate_limited(request):
    address = _client_address(request)
    key = f'reservation-rate:{address}'
    if cache.add(key, 1, timeout=600):
        return False
    try:
        return cache.incr(key) > 5
    except ValueError:
        cache.set(key, 1, timeout=600)
        return False


@require_POST
def create_reservation(request):
    language = request.session.get('site_language', 'ar')
    if _reservation_rate_limited(request):
        message = 'محاولات كثيرة. يرجى الانتظار قليلًا ثم المحاولة مجددًا.' if language == 'ar' else 'Too many attempts. Please wait a few minutes and try again.'
        response = HttpResponse(message, status=429)
        response['Retry-After'] = '600'
        return response

    site = RestaurantSettings.load()
    form = ReservationForm(request.POST, language=language, site=site)
    if not form.is_valid():
        request.session['reservation_draft'] = {
            field: request.POST.get(field, '') for field in form.fields
        }
        messages.error(request, 'يرجى مراجعة بيانات الحجز.' if language == 'ar' else 'Please review the reservation details.')
        return redirect(f"{reverse('restaurant:home')}?lang={language}#contact")

    number = ''.join(ch for ch in site.whatsapp_number if ch.isdigit())
    if not number:
        request.session['reservation_draft'] = {
            field: request.POST.get(field, '') for field in form.fields
        }
        messages.error(request, 'رقم واتساب غير مضبوط.' if language == 'ar' else 'WhatsApp number is not configured.')
        return redirect(f"{reverse('restaurant:home')}?lang={language}#contact")

    with transaction.atomic():
        locked_site = RestaurantSettings.objects.select_for_update().get(pk=site.pk)
        form = ReservationForm(request.POST, language=language, site=locked_site)
        if not form.is_valid():
            request.session['reservation_draft'] = {
                field: request.POST.get(field, '') for field in form.fields
            }
            messages.error(request, 'يرجى مراجعة بيانات الحجز.' if language == 'ar' else 'Please review the reservation details.')
            return redirect(f"{reverse('restaurant:home')}?lang={language}#contact")
        duplicate_exists = Reservation.objects.filter(
            phone=form.cleaned_data['phone'],
            date=form.cleaned_data['date'],
            time=form.cleaned_data['time'],
            status__in=['new', 'contacted', 'confirmed'],
        ).exists()
        if duplicate_exists:
            request.session['reservation_draft'] = {
                field: request.POST.get(field, '') for field in form.fields
            }
            messages.error(request, 'يوجد حجز مطابق مسجل بالفعل.' if language == 'ar' else 'An identical reservation already exists.')
            return redirect(f"{reverse('restaurant:home')}?lang={language}#contact")
        reservation = form.save()

    _notify_new_reservation(reservation)
    if language == 'ar':
        text = (
            'مرحبًا B12، أرسلت طلب حجز طاولة عبر الموقع:\n'
            f'الاسم: {reservation.full_name}\n'
            f'الهاتف: {reservation.phone}\n'
            f'التاريخ: {reservation.date}\n'
            f'الوقت: {reservation.time.strftime("%H:%M")}\n'
            f'عدد الأشخاص: {reservation.guests}\n'
            f'المناسبة: {reservation.occasion or "لا يوجد"}\n'
            f'ملاحظات: {reservation.notes or "لا يوجد"}'
        )
    else:
        text = (
            'Hello B12, I submitted a table reservation request on the website:\n'
            f'Name: {reservation.full_name}\n'
            f'Phone: {reservation.phone}\n'
            f'Date: {reservation.date}\n'
            f'Time: {reservation.time.strftime("%H:%M")}\n'
            f'Guests: {reservation.guests}\n'
            f'Occasion: {reservation.occasion or "None"}\n'
            f'Notes: {reservation.notes or "None"}'
        )
    return redirect(f'https://wa.me/{number}?text={quote(text)}')


def _notify_new_reservation(reservation):
    recipient = getattr(settings, 'RESERVATION_NOTIFY_EMAIL', '')
    if not recipient or not settings.EMAIL_HOST:
        return
    try:
        send_mail(
            subject=f'حجز جديد: {reservation.full_name} - {reservation.date}',
            message=(
                f'الاسم: {reservation.full_name}\n'
                f'الهاتف: {reservation.phone}\n'
                f'التاريخ: {reservation.date}\n'
                f'الوقت: {reservation.time.strftime("%H:%M")}\n'
                f'عدد الأشخاص: {reservation.guests}\n'
                f'المناسبة: {reservation.occasion or "لا يوجد"}\n'
                f'ملاحظات: {reservation.notes or "لا يوجد"}'
            ),
            from_email=None,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        logger.exception('Failed to send reservation notification for reservation %s', reservation.pk)


@require_GET
def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse('restaurant:sitemap'))
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        'Disallow: /o/',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


@require_GET
def sitemap_xml(request):
    home_url = request.build_absolute_uri(reverse('restaurant:home'))
    menu_url = request.build_absolute_uri(reverse('restaurant:menu'))
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        '  <url>\n'
        f'    <loc>{home_url}</loc>\n'
        f'    <xhtml:link rel="alternate" hreflang="ar" href="{home_url}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="en" href="{home_url}?lang=en"/>\n'
        '  </url>\n'
        '  <url>\n'
        f'    <loc>{menu_url}</loc>\n'
        f'    <xhtml:link rel="alternate" hreflang="ar" href="{menu_url}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="en" href="{menu_url}?lang=en"/>\n'
        '  </url>\n'
        '</urlset>'
    )
    return HttpResponse(xml, content_type='application/xml')
