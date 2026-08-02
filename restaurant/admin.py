from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    FAQ,
    HeroStat,
    MenuItem,
    MenuItemSize,
    Offer,
    Order,
    OrderLine,
    Reservation,
    RestaurantSettings,
    Service,
    SocialPost,
    Testimonial,
)


def _relative_luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    converted = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * converted[0] + 0.7152 * converted[1] + 0.0722 * converted[2]


def _contrast_ratio(first, second):
    brighter, darker = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (brighter + 0.05) / (darker + 0.05)


class RestaurantSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = RestaurantSettings
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        # Each colour is checked against the text colour it actually carries on
        # the page, not against a fixed reference. The two reds are backgrounds
        # for white text; the warm colours and the light surfaces are
        # backgrounds for dark ink. Checking yellow against white would demand a
        # yellow no customer would recognise as the brand's.
        checks = [
            ('primary_color', '#FFFFFF', 'الأحمر الأساسي يجب أن يكون واضحًا مع النص الأبيض فوقه.'),
            ('deep_color', '#FFFFFF', 'الأحمر الداكن يجب أن يكون واضحًا مع النص الأبيض فوقه.'),
            ('gold_color', '#222222', 'الأصفر المميز يجب أن يكون واضحًا مع النص الداكن فوقه.'),
            ('orange_color', '#222222', 'البرتقالي يجب أن يكون واضحًا مع النص الداكن فوقه.'),
            ('background_color', '#222222', 'خلفية الصفحة يجب أن تكون واضحة مع النص الداكن فوقها.'),
            ('surface_color', '#222222', 'لون البطاقات يجب أن يكون واضحًا مع النص الداكن فوقه.'),
            ('whatsapp_color', '#222222', 'لون واتساب يجب أن يكون واضحًا مع النص الداكن فوقه.'),
        ]
        for field_name, text_color, message in checks:
            value = cleaned.get(field_name)
            if value and _contrast_ratio(value, text_color) < 4.5:
                self.add_error(field_name, message)
        return cleaned


admin.site.site_header = 'فرايز ستيشن — لوحة الإدارة'
admin.site.site_title = 'Fries Station Admin'
admin.site.index_title = 'إدارة الموقع والمحتوى والطلبات'


class ImagePreviewMixin:
    @admin.display(description='معاينة')
    def image_preview(self, obj):
        src = getattr(obj, 'image_src', '') or ''
        if not src:
            return '—'
        return format_html(
            '<img src="{}" style="width:74px;height:54px;object-fit:cover;border-radius:8px;border:1px solid #d3cfcc" alt="">',
            src,
        )


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    form = RestaurantSettingsAdminForm
    fieldsets = (
        ('الهوية', {'fields': ('name_ar', 'name_en', 'tagline_ar', 'tagline_en', 'logo')}),
        ('ألوان الهوية', {'fields': (
            ('primary_color', 'gold_color'),
            ('deep_color', 'orange_color'),
            ('background_color', 'surface_color'),
            'whatsapp_color',
        )}),
        ('واجهة الصفحة الرئيسية', {'fields': (
            ('hero_title_ar', 'hero_title_en'),
            ('hero_text_ar', 'hero_text_en'),
            'hero_image',
            'hero_image_url',
            'og_image',
            'og_image_url',
        )}),
        ('قسم من نحن', {'fields': (
            ('about_title_ar', 'about_title_en'),
            ('about_text_ar', 'about_text_en'),
        )}),
        ('الأزرار الرئيسية', {'fields': (
            ('order_cta_ar', 'order_cta_en'),
            ('menu_cta_ar', 'menu_cta_en'),
            ('whatsapp_panel_text_ar', 'whatsapp_panel_text_en'),
        )}),
        ('عناوين أقسام الصفحة', {'fields': (
            ('menu_title_ar', 'menu_title_en'),
            ('featured_title_ar', 'featured_title_en'),
            ('offers_title_ar', 'offers_title_en'),
            ('services_title_ar', 'services_title_en'),
            ('reviews_title_ar', 'reviews_title_en'),
            ('reservation_title_ar', 'reservation_title_en'),
            ('reservation_text_ar', 'reservation_text_en'),
            ('faq_title_ar', 'faq_title_en'),
            ('social_title_ar', 'social_title_en'),
        )}),
        ('بيانات التواصل', {'fields': (
            'whatsapp_number', 'phone', 'email',
            ('address_ar', 'address_en'),
            ('hours_ar', 'hours_en'),
            'currency',
        )}),
        ('ضوابط الحجز', {'fields': (
            ('reservation_open_time', 'reservation_close_time'),
            ('reservation_slot_minutes', 'max_reservations_per_slot'),
            'max_reservation_days_ahead',
        )}),
        ('التواصل الاجتماعي والتذييل', {'fields': (
            'instagram_url', 'facebook_url', 'tiktok_url',
            ('footer_text_ar', 'footer_text_en'),
        )}),
        ('SEO والمشاركة', {'classes': ('collapse',), 'fields': (
            ('seo_title_ar', 'seo_title_en'),
            ('seo_description_ar', 'seo_description_en'),
        )}),
        ('إظهار وإخفاء الأقسام', {'fields': (
            'show_about', 'show_categories', 'show_featured', 'show_offers', 'show_services',
            'show_reviews', 'show_reservation', 'show_faq', 'show_social',
        )}),
    )

    def has_add_permission(self, request):
        return not RestaurantSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroStat)
class HeroStatAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'title_en', 'icon', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title_ar', 'title_en')


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('name_ar', 'name_en', 'price', 'is_featured', 'is_available', 'display_order')
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('image_preview', 'name_ar', 'name_en', 'slug', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('name_ar', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [MenuItemInline]


class MenuItemSizeInline(admin.TabularInline):
    model = MenuItemSize
    extra = 0
    fields = ('name_ar', 'name_en', 'price', 'display_order', 'is_available')


@admin.register(MenuItem)
class MenuItemAdmin(ImagePreviewMixin, admin.ModelAdmin):
    inlines = [MenuItemSizeInline]
    list_display = (
        'image_preview', 'name_ar', 'category', 'price', 'old_price',
        'is_featured', 'is_available', 'display_order',
    )
    list_filter = ('category', 'is_featured', 'is_available')
    list_editable = ('price', 'is_featured', 'is_available', 'display_order')
    search_fields = ('name_ar', 'name_en', 'description_ar', 'description_en')
    autocomplete_fields = ('category',)
    list_select_related = ('category',)


@admin.register(Offer)
class OfferAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('image_preview', 'title_ar', 'price_text_ar', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title_ar', 'title_en')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'title_en', 'icon', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title_ar', 'title_en')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'display_order', 'is_active')
    list_editable = ('rating', 'display_order', 'is_active')
    search_fields = ('customer_name', 'review_ar', 'review_en')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_ar', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('question_ar', 'question_en', 'answer_ar', 'answer_en')


@admin.register(SocialPost)
class SocialPostAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    search_fields = ('title',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'date', 'time', 'guests', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    list_editable = ('status',)
    search_fields = ('full_name', 'phone', 'occasion', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 0
    # Prices were computed by the server at order time; showing them as text
    # keeps the admin from becoming a second, weaker way to re-price an order.
    readonly_fields = ('name_ar', 'size_label_ar', 'quantity', 'unit_price', 'is_priced', 'price_note')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'source', 'customer_name', 'customer_count', 'table_number',
        'fulfillment', 'total', 'status', 'created_at',
    )
    list_filter = ('source', 'status', 'fulfillment', 'created_at')
    search_fields = ('code', 'customer_name', 'phone', 'table_number', 'notes')
    readonly_fields = (
        'code', 'token', 'source', 'cashier', 'total', 'has_unpriced_lines',
        'currency', 'created_at', 'updated_at',
    )
    inlines = [OrderLineInline]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        # Orders are created by customers through the site, never by hand.
        return False
