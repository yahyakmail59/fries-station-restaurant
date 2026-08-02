"""Section registry for the control panel.

Every content model the restaurant edits is described here once — its
columns, its search fields and its form — and the generic views in
views_panel.py render all of them. Adding a model to the panel means
adding one entry, not a new view and template.

Django's own admin stays registered as a fallback for user accounts and
passwords, which this panel deliberately does not touch.
"""
from django.db import models as django_models

from .models import (
    Category,
    FAQ,
    HeroStat,
    MenuItem,
    MenuItemSize,
    Offer,
    Order,
    Reservation,
    Service,
    SocialPost,
    Testimonial,
)


SECTIONS = {
    'orders': {
        'model': Order,
        'title': 'الطلبات',
        'singular': 'طلب',
        'group': 'الحجوزات',
        'icon': 'bag',
        'columns': [
            ('code', 'الرقم'),
            ('source', 'المصدر'),
            ('customer_name', 'العميل'),
            ('customer_count', 'الزبائن'),
            ('fulfillment', 'الاستلام'),
            ('total', 'الإجمالي'),
            ('status', 'الحالة'),
            ('created_at', 'التاريخ'),
        ],
        'search': ('code', 'customer_name', 'phone', 'table_number', 'notes'),
        'ordering': ('-created_at',),
        'toggles': (),
        # Totals are computed by the server at order time; staff move the
        # order through its statuses, they do not re-price it here.
        'form_fields': ('status', 'fulfillment', 'customer_name', 'phone', 'address', 'notes'),
        'can_add': False,
        'detail_url': 'restaurant:order_detail',
        'detail_field': 'token',
    },
    'reservations': {
        'model': Reservation,
        'title': 'الحجوزات',
        'singular': 'حجز',
        'group': 'الحجوزات',
        'icon': 'calendar',
        'columns': [
            ('full_name', 'الاسم'),
            ('phone', 'الهاتف'),
            ('date', 'التاريخ'),
            ('time', 'الوقت'),
            ('guests', 'الضيوف'),
            ('status', 'الحالة'),
        ],
        'search': ('full_name', 'phone', 'occasion', 'notes'),
        'ordering': ('-date', '-time'),
        'toggles': (),
        'can_add': True,
    },
    'menu': {
        'model': MenuItem,
        'title': 'الأطباق',
        'singular': 'طبق',
        'group': 'المحتوى',
        'icon': 'dish',
        'columns': [
            ('image_src', 'الصورة'),
            ('name_ar', 'الاسم'),
            ('category', 'القسم'),
            ('price', 'السعر'),
            ('is_featured', 'مميز'),
            ('is_available', 'متاح'),
            ('display_order', 'الترتيب'),
        ],
        'search': ('name_ar', 'name_en', 'description_ar', 'description_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_featured', 'is_available'),
        'related': ('category',),
        'can_add': True,
    },
    'sizes': {
        'model': MenuItemSize,
        'title': 'أحجام الأصناف',
        'singular': 'حجم',
        'group': 'المحتوى',
        'icon': 'grid',
        'columns': [
            ('menu_item', 'الصنف'),
            ('name_ar', 'الحجم'),
            ('price', 'السعر'),
            ('display_order', 'الترتيب'),
            ('is_available', 'متاح'),
        ],
        'search': ('name_ar', 'name_en', 'menu_item__name_ar'),
        'ordering': ('menu_item__display_order', 'display_order', 'id'),
        'toggles': ('is_available',),
        'related': ('menu_item',),
        'can_add': True,
    },
    'categories': {
        'model': Category,
        'title': 'أقسام القائمة',
        'singular': 'قسم',
        'group': 'المحتوى',
        'icon': 'grid',
        'columns': [
            ('image_src', 'الصورة'),
            ('name_ar', 'الاسم'),
            ('name_en', 'بالإنجليزية'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('name_ar', 'name_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'offers': {
        'model': Offer,
        'title': 'العروض',
        'singular': 'عرض',
        'group': 'المحتوى',
        'icon': 'tag',
        'columns': [
            ('image_src', 'الصورة'),
            ('title_ar', 'العنوان'),
            ('price_text_ar', 'السعر'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('title_ar', 'title_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'services': {
        'model': Service,
        'title': 'الخدمات',
        'singular': 'خدمة',
        'group': 'المحتوى',
        'icon': 'spark',
        'columns': [
            ('title_ar', 'العنوان'),
            ('icon', 'الأيقونة'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('title_ar', 'title_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'reviews': {
        'model': Testimonial,
        'title': 'آراء العملاء',
        'singular': 'رأي',
        'group': 'المحتوى',
        'icon': 'star',
        'columns': [
            ('customer_name', 'العميل'),
            ('rating', 'النجوم'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('customer_name', 'review_ar', 'review_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'faq': {
        'model': FAQ,
        'title': 'الأسئلة الشائعة',
        'singular': 'سؤال',
        'group': 'المحتوى',
        'icon': 'help',
        'columns': [
            ('question_ar', 'السؤال'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('question_ar', 'question_en', 'answer_ar', 'answer_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'social': {
        'model': SocialPost,
        'title': 'صور إنستغرام',
        'singular': 'صورة',
        'group': 'المحتوى',
        'icon': 'image',
        'columns': [
            ('image_src', 'الصورة'),
            ('title', 'العنوان'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('title',),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
    'hero': {
        'model': HeroStat,
        'title': 'ميزات الواجهة',
        'singular': 'ميزة',
        'group': 'المحتوى',
        'icon': 'spark',
        'columns': [
            ('title_ar', 'العنوان'),
            ('icon', 'الأيقونة'),
            ('display_order', 'الترتيب'),
            ('is_active', 'ظاهر'),
        ],
        'search': ('title_ar', 'title_en'),
        'ordering': ('display_order', 'id'),
        'toggles': ('is_active',),
        'can_add': True,
    },
}


# Field groups for the single settings record, mirroring how the page reads
# top to bottom rather than how the model is declared.
SETTINGS_GROUPS = [
    ('الهوية', ('name_ar', 'name_en', 'tagline_ar', 'tagline_en', 'logo', 'currency')),
    ('واجهة الصفحة', ('hero_title_ar', 'hero_title_en', 'hero_text_ar', 'hero_text_en',
                      'hero_image', 'hero_image_url', 'og_image', 'og_image_url')),
    ('التواصل', ('whatsapp_number', 'phone', 'email', 'address_ar', 'address_en',
                 'hours_ar', 'hours_en', 'instagram_url', 'facebook_url', 'tiktok_url')),
    ('تشغيل الطلبات', ('delivery_enabled',)),
    ('ضوابط الحجز', ('reservation_open_time', 'reservation_close_time',
                     'reservation_slot_minutes', 'max_reservations_per_slot',
                     'max_reservation_days_ahead')),
    ('الألوان', ('primary_color', 'gold_color', 'deep_color', 'orange_color',
                 'background_color', 'surface_color', 'whatsapp_color')),
    ('قسم من نحن', ('about_title_ar', 'about_title_en', 'about_text_ar', 'about_text_en')),
    ('الأزرار', ('order_cta_ar', 'order_cta_en', 'menu_cta_ar', 'menu_cta_en',
                 'whatsapp_panel_text_ar', 'whatsapp_panel_text_en')),
    ('عناوين الأقسام', ('menu_title_ar', 'menu_title_en', 'featured_title_ar', 'featured_title_en',
                        'offers_title_ar', 'offers_title_en', 'services_title_ar', 'services_title_en',
                        'reviews_title_ar', 'reviews_title_en', 'reservation_title_ar', 'reservation_title_en',
                        'reservation_text_ar', 'reservation_text_en', 'faq_title_ar', 'faq_title_en',
                        'social_title_ar', 'social_title_en')),
    ('إظهار الأقسام', ('show_about', 'show_categories', 'show_featured', 'show_offers',
                       'show_services', 'show_reviews', 'show_reservation', 'show_faq', 'show_social')),
    ('محركات البحث والتذييل', ('seo_title_ar', 'seo_title_en', 'seo_description_ar',
                               'seo_description_en', 'footer_text_ar', 'footer_text_en')),
]


def get_section(slug):
    return SECTIONS.get(slug)


def perm(section, action):
    """The Django permission code for an action on a section's model."""
    meta = section['model']._meta
    return f'{meta.app_label}.{action}_{meta.model_name}'


def cell(obj, field):
    """Render one list cell, picking a shape from the underlying field."""
    if field == 'image_src':
        return {'type': 'image', 'url': getattr(obj, 'image_src', '') or ''}

    value = getattr(obj, field, None)
    try:
        model_field = obj._meta.get_field(field)
    except Exception:
        return {'type': 'text', 'value': '' if value is None else str(value)}

    if model_field.choices:
        return {'type': 'text', 'value': getattr(obj, f'get_{field}_display')()}
    if isinstance(model_field, django_models.BooleanField):
        return {'type': 'bool', 'on': bool(value), 'field': field}
    if isinstance(model_field, django_models.ImageField):
        return {'type': 'image', 'url': value.url if value else ''}
    if isinstance(model_field, django_models.DecimalField):
        return {'type': 'text', 'value': f'{value:g}' if value is not None else ''}
    if value is None:
        return {'type': 'text', 'value': ''}
    return {'type': 'text', 'value': str(value)}


def nav(user, active=''):
    """Sidebar entries the signed-in user is actually allowed to open."""
    groups = {}
    for slug, section in SECTIONS.items():
        if not user.has_perm(perm(section, 'view')) and not user.has_perm(perm(section, 'change')):
            continue
        groups.setdefault(section['group'], []).append({
            'slug': slug,
            'title': section['title'],
            'icon': section['icon'],
            'is_active': active == slug,
        })
    return groups
