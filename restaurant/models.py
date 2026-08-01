from datetime import time
from decimal import Decimal
import unicodedata
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, URLValidator
from django.db import models
from django.utils.text import slugify


hex_color_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.',
)

absolute_url_validator = URLValidator(schemes=['http', 'https'])


def image_source_validator(value):
    """Accept an external HTTP(S) URL or a safe local static/media path."""
    if not value:
        return
    if value.startswith(('/static/', '/media/')):
        if '..' in value.split('/'):
            raise ValidationError('مسار الصورة المحلي غير صالح.')
        return
    try:
        absolute_url_validator(value)
    except ValidationError as exc:
        raise ValidationError(
            'أدخل رابط HTTP(S) كاملًا أو مسارًا محليًا يبدأ بـ /static/ أو /media/.'
        ) from exc
    if urlsplit(value).username or urlsplit(value).password:
        raise ValidationError('رابط الصورة لا يجوز أن يحتوي على بيانات دخول.')


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        abstract = True


class RestaurantSettings(TimeStampedModel):
    name_ar = models.CharField(max_length=120, default='مطعم B12', verbose_name='اسم المطعم بالعربية')
    name_en = models.CharField(max_length=120, default='B12 Restaurant', verbose_name='اسم المطعم بالإنجليزية')
    tagline_ar = models.CharField(max_length=160, default='الطعم حكاية', verbose_name='الشعار النصي بالعربية')
    tagline_en = models.CharField(max_length=160, default='Taste Tells a Story', verbose_name='الشعار النصي بالإنجليزية')
    hero_title_ar = models.CharField(max_length=180, default='الطعم حكاية', verbose_name='عنوان الواجهة بالعربية')
    hero_title_en = models.CharField(max_length=180, default='Taste Tells a Story', verbose_name='عنوان الواجهة بالإنجليزية')
    hero_text_ar = models.TextField(default='رحلة من النكهات الشرقية والعالمية محضّرة بأجود المكونات وبلمسة استثنائية.', verbose_name='وصف الواجهة بالعربية')
    hero_text_en = models.TextField(default='A journey of global and oriental flavours crafted with premium ingredients and passion.', verbose_name='وصف الواجهة بالإنجليزية')
    logo = models.ImageField(upload_to='branding/', blank=True, verbose_name='الشعار')
    hero_image = models.ImageField(upload_to='branding/', blank=True, verbose_name='صورة الواجهة')
    hero_image_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[image_source_validator],
        verbose_name='رابط أو مسار صورة الواجهة البديل',
    )
    og_image = models.ImageField(upload_to='branding/', blank=True, verbose_name='صورة المشاركة الاجتماعية')

    primary_color = models.CharField(max_length=20, default='#E30613', validators=[hex_color_validator], verbose_name='اللون الأحمر الرئيسي')
    gold_color = models.CharField(max_length=20, default='#D4AF37', validators=[hex_color_validator], verbose_name='اللون الذهبي')
    background_color = models.CharField(max_length=20, default='#050505', validators=[hex_color_validator], verbose_name='لون الخلفية')
    surface_color = models.CharField(max_length=20, default='#111111', validators=[hex_color_validator], verbose_name='لون البطاقات')
    whatsapp_color = models.CharField(max_length=20, default='#25D366', validators=[hex_color_validator], verbose_name='لون واتساب')

    about_title_ar = models.CharField(max_length=160, default='من نحن', verbose_name='عنوان من نحن بالعربية')
    about_title_en = models.CharField(max_length=160, default='About Us', verbose_name='عنوان من نحن بالإنجليزية')
    about_text_ar = models.TextField(
        default='وُلد مطعم B12 من شغف حقيقي بالطعم الأصيل. نجمع بين المشاوي الشرقية والأطباق العالمية في مكان واحد، ونحضّر كل طبق يوميًا بمكونات طازجة مختارة بعناية، لنقدم لكم تجربة تستحق التكرار.',
        verbose_name='نص من نحن بالعربية',
    )
    about_text_en = models.TextField(
        default='B12 was born from a real passion for authentic flavour. We bring oriental grills and international dishes together under one roof, preparing every dish daily with carefully selected fresh ingredients.',
        verbose_name='نص من نحن بالإنجليزية',
    )

    menu_title_ar = models.CharField(max_length=160, default='استكشف أقسام القائمة', verbose_name='عنوان أقسام القائمة بالعربية')
    menu_title_en = models.CharField(max_length=160, default='Explore Our Menu', verbose_name='عنوان أقسام القائمة بالإنجليزية')
    featured_title_ar = models.CharField(max_length=160, default='أطباق مميزة', verbose_name='عنوان الأطباق المميزة بالعربية')
    featured_title_en = models.CharField(max_length=160, default='Featured Menu', verbose_name='عنوان الأطباق المميزة بالإنجليزية')
    offers_title_ar = models.CharField(max_length=160, default='عروض وأطباق مميزة', verbose_name='عنوان العروض بالعربية')
    offers_title_en = models.CharField(max_length=160, default='Special Offers', verbose_name='عنوان العروض بالإنجليزية')
    services_title_ar = models.CharField(max_length=160, default='خدماتنا', verbose_name='عنوان الخدمات بالعربية')
    services_title_en = models.CharField(max_length=160, default='Our Services', verbose_name='عنوان الخدمات بالإنجليزية')
    reviews_title_ar = models.CharField(max_length=160, default='آراء عملائنا', verbose_name='عنوان التقييمات بالعربية')
    reviews_title_en = models.CharField(max_length=160, default='Customer Reviews', verbose_name='عنوان التقييمات بالإنجليزية')
    reservation_title_ar = models.CharField(max_length=180, default='احجز طاولتك أو تواصل معنا', verbose_name='عنوان الحجز بالعربية')
    reservation_title_en = models.CharField(max_length=180, default='Reservation & Contact', verbose_name='عنوان الحجز بالإنجليزية')
    reservation_text_ar = models.TextField(default='احجز طاولتك بسهولة أو تواصل معنا مباشرة عبر واتساب.', verbose_name='وصف الحجز بالعربية')
    reservation_text_en = models.TextField(default='Reserve your table easily or contact us directly on WhatsApp.', verbose_name='وصف الحجز بالإنجليزية')
    faq_title_ar = models.CharField(max_length=160, default='الأسئلة الشائعة', verbose_name='عنوان الأسئلة بالعربية')
    faq_title_en = models.CharField(max_length=160, default='FAQ', verbose_name='عنوان الأسئلة بالإنجليزية')
    social_title_ar = models.CharField(max_length=160, default='تابعنا على إنستغرام', verbose_name='عنوان التواصل الاجتماعي بالعربية')
    social_title_en = models.CharField(max_length=160, default='Follow Us on Instagram', verbose_name='عنوان التواصل الاجتماعي بالإنجليزية')

    order_cta_ar = models.CharField(max_length=100, default='اطلب الآن عبر واتساب', verbose_name='نص زر الطلب بالعربية')
    order_cta_en = models.CharField(max_length=100, default='Order on WhatsApp', verbose_name='نص زر الطلب بالإنجليزية')
    menu_cta_ar = models.CharField(max_length=100, default='استعرض القائمة', verbose_name='نص زر القائمة بالعربية')
    menu_cta_en = models.CharField(max_length=100, default='View Menu', verbose_name='نص زر القائمة بالإنجليزية')
    whatsapp_panel_text_ar = models.CharField(max_length=180, default='خدمة سريعة، رد فوري، وطلب سهل.', verbose_name='وصف صندوق واتساب بالعربية')
    whatsapp_panel_text_en = models.CharField(max_length=180, default='Fast service, quick reply and an easy order.', verbose_name='وصف صندوق واتساب بالإنجليزية')

    seo_title_ar = models.CharField(max_length=180, blank=True, verbose_name='عنوان SEO بالعربية')
    seo_title_en = models.CharField(max_length=180, blank=True, verbose_name='عنوان SEO بالإنجليزية')
    seo_description_ar = models.TextField(blank=True, verbose_name='وصف SEO بالعربية')
    seo_description_en = models.TextField(blank=True, verbose_name='وصف SEO بالإنجليزية')
    footer_text_ar = models.CharField(max_length=255, default='رحلة من النكهات العالمية والشرقية الأصلية.', verbose_name='وصف التذييل بالعربية')
    footer_text_en = models.CharField(max_length=255, default='A journey of authentic global and oriental flavours.', verbose_name='وصف التذييل بالإنجليزية')

    whatsapp_number = models.CharField(max_length=30, default='972597862389', help_text='أرقام فقط مع رمز الدولة، مثال: 972597862389', verbose_name='رقم واتساب')
    phone = models.CharField(max_length=40, default='+972 59 786 2389', verbose_name='رقم الهاتف')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    address_ar = models.CharField(max_length=255, default='غرب غزة - دوار حيدر', verbose_name='العنوان بالعربية')
    address_en = models.CharField(max_length=255, default='West Gaza - Haidar Roundabout', verbose_name='العنوان بالإنجليزية')
    hours_ar = models.CharField(max_length=160, default='يوميًا من 8 صباحًا حتى 2 صباحًا', verbose_name='ساعات العمل بالعربية')
    hours_en = models.CharField(max_length=160, default='Daily, 8:00 AM - 2:00 AM', verbose_name='ساعات العمل بالإنجليزية')
    currency = models.CharField(max_length=20, default='₪', verbose_name='رمز العملة')
    instagram_url = models.URLField(blank=True, verbose_name='رابط إنستغرام')
    facebook_url = models.URLField(blank=True, verbose_name='رابط فيسبوك')

    show_about = models.BooleanField(default=True, verbose_name='إظهار قسم من نحن')
    show_categories = models.BooleanField(default=True, verbose_name='إظهار أقسام القائمة')
    show_featured = models.BooleanField(default=True, verbose_name='إظهار قائمة الأطباق')
    show_offers = models.BooleanField(default=True, verbose_name='إظهار العروض')
    show_services = models.BooleanField(default=True, verbose_name='إظهار الخدمات')
    show_reviews = models.BooleanField(default=True, verbose_name='إظهار آراء العملاء')
    show_reservation = models.BooleanField(default=True, verbose_name='إظهار الحجز والتواصل')
    show_faq = models.BooleanField(default=True, verbose_name='إظهار الأسئلة الشائعة')
    show_social = models.BooleanField(default=True, verbose_name='إظهار معرض التواصل الاجتماعي')

    reservation_open_time = models.TimeField(
        default=time(8, 0),
        verbose_name='بداية استقبال الحجوزات',
    )
    reservation_close_time = models.TimeField(
        default=time(2, 0),
        verbose_name='نهاية استقبال الحجوزات',
        help_text='يمكن أن تكون بعد منتصف الليل، مثل 02:00.',
    )
    reservation_slot_minutes = models.PositiveSmallIntegerField(
        default=30,
        choices=[(15, '15 دقيقة'), (30, '30 دقيقة'), (60, '60 دقيقة')],
        verbose_name='مدة فترة الحجز',
    )
    max_reservations_per_slot = models.PositiveSmallIntegerField(
        default=6,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name='الحد الأقصى للحجوزات في الفترة',
    )
    max_reservation_days_ahead = models.PositiveSmallIntegerField(
        default=90,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='أقصى عدد أيام للحجز المسبق',
    )

    class Meta:
        verbose_name = 'إعدادات المطعم'
        verbose_name_plural = 'إعدادات المطعم'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def display_phone(self):
        """Remove invisible bidi controls that can leak into copied numbers."""
        return ''.join(
            character
            for character in self.phone
            if unicodedata.category(character) != 'Cf'
        ).strip()

    @property
    def tel_phone(self):
        """Return a dial-safe phone value while keeping the formatted label."""
        display_phone = self.display_phone
        digits = ''.join(character for character in display_phone if character.isdigit())
        return f'+{digits}' if display_phone.startswith('+') else digits

    @property
    def hero_image_src(self):
        if self.hero_image:
            return self.hero_image.url
        return self.hero_image_url

    @property
    def hero_image_mobile_src(self):
        if self.hero_image:
            return ''
        if self.hero_image_url.endswith('/hero-b12.webp'):
            return self.hero_image_url.removesuffix('.webp') + '-960.webp'
        return ''

    @property
    def og_image_src(self):
        if self.og_image:
            return self.og_image.url
        return self.hero_image_src

    def __str__(self):
        return self.name_ar


class HeroStat(TimeStampedModel):
    ICON_CHOICES = [
        ('leaf', 'ورقة / مكونات'),
        ('clock', 'ساعة / سرعة'),
        ('crown', 'تاج / جودة'),
        ('fire', 'نار / شواية'),
        ('star', 'نجمة'),
    ]
    title_ar = models.CharField(max_length=100, verbose_name='العنوان بالعربية')
    title_en = models.CharField(max_length=100, verbose_name='العنوان بالإنجليزية')
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='leaf', verbose_name='الأيقونة')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'ميزة في الواجهة'
        verbose_name_plural = 'ميزات الواجهة'

    @property
    def lucide_icon(self):
        return {
            'leaf': 'leaf',
            'clock': 'timer',
            'crown': 'crown',
            'fire': 'flame',
            'star': 'star',
        }.get(self.icon, 'sparkles')

    def __str__(self):
        return self.title_ar


class Category(TimeStampedModel):
    ICON_CHOICES = [
        ('skewer', 'شرقي / مشاوي'),
        ('burger', 'غربي / برجر'),
        ('pasta', 'إيطالي / باستا'),
        ('pizza', 'بيتزا'),
        ('drink', 'مشروبات'),
        ('dessert', 'حلويات'),
        ('fish', 'بحريات'),
        ('salad', 'سلطات'),
    ]
    name_ar = models.CharField(max_length=100, verbose_name='الاسم بالعربية')
    name_en = models.CharField(max_length=100, verbose_name='الاسم بالإنجليزية')
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True, verbose_name='الرابط المختصر')
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='burger', verbose_name='الأيقونة')
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name='الصورة')
    image_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[image_source_validator],
        verbose_name='رابط أو مسار صورة بديل',
    )
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'قسم قائمة الطعام'
        verbose_name_plural = 'أقسام قائمة الطعام'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_en or self.name_ar, allow_unicode=True) or 'category'
            candidate = base
            counter = 2
            while Category.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f'{base}-{counter}'
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def lucide_icon(self):
        return {
            'skewer': 'flame',
            'burger': 'sandwich',
            'pasta': 'soup',
            'pizza': 'pizza',
            'drink': 'cup-soda',
            'dessert': 'cake-slice',
            'fish': 'fish',
            'salad': 'salad',
        }.get(self.icon, 'utensils')

    def __str__(self):
        return self.name_ar


class MenuItem(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items', verbose_name='القسم')
    name_ar = models.CharField(max_length=150, verbose_name='اسم الطبق بالعربية')
    name_en = models.CharField(max_length=150, verbose_name='اسم الطبق بالإنجليزية')
    description_ar = models.TextField(blank=True, verbose_name='الوصف بالعربية')
    description_en = models.TextField(blank=True, verbose_name='الوصف بالإنجليزية')
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='السعر')
    old_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='السعر القديم')
    image = models.ImageField(upload_to='menu_items/', blank=True, verbose_name='الصورة')
    image_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[image_source_validator],
        verbose_name='رابط أو مسار صورة بديل',
    )
    badge_ar = models.CharField(max_length=50, blank=True, verbose_name='شارة بالعربية')
    badge_en = models.CharField(max_length=50, blank=True, verbose_name='شارة بالإنجليزية')
    is_featured = models.BooleanField(default=False, verbose_name='طبق مميز')
    is_available = models.BooleanField(default=True, verbose_name='متاح')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'طبق'
        verbose_name_plural = 'الأطباق'
        indexes = [
            models.Index(fields=['is_available', 'is_featured']),
            models.Index(fields=['category', 'display_order']),
        ]

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name_ar


class Offer(TimeStampedModel):
    title_ar = models.CharField(max_length=150, verbose_name='العنوان بالعربية')
    title_en = models.CharField(max_length=150, verbose_name='العنوان بالإنجليزية')
    description_ar = models.TextField(blank=True, verbose_name='الوصف بالعربية')
    description_en = models.TextField(blank=True, verbose_name='الوصف بالإنجليزية')
    price_text_ar = models.CharField(max_length=80, blank=True, verbose_name='نص السعر بالعربية')
    price_text_en = models.CharField(max_length=80, blank=True, verbose_name='نص السعر بالإنجليزية')
    image = models.ImageField(upload_to='offers/', blank=True, verbose_name='الصورة')
    image_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[image_source_validator],
        verbose_name='رابط أو مسار صورة بديل',
    )
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'عرض'
        verbose_name_plural = 'العروض'

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.title_ar


class Service(TimeStampedModel):
    ICON_CHOICES = [
        ('dine', 'تناول في المطعم'),
        ('bag', 'طلبات خارجية'),
        ('scooter', 'توصيل'),
        ('whatsapp', 'واتساب'),
        ('leaf', 'مكونات'),
        ('clock', 'سرعة'),
    ]
    title_ar = models.CharField(max_length=100, verbose_name='العنوان بالعربية')
    title_en = models.CharField(max_length=100, verbose_name='العنوان بالإنجليزية')
    description_ar = models.CharField(max_length=180, blank=True, verbose_name='الوصف بالعربية')
    description_en = models.CharField(max_length=180, blank=True, verbose_name='الوصف بالإنجليزية')
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='dine', verbose_name='الأيقونة')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'

    @property
    def lucide_icon(self):
        return {
            'dine': 'utensils',
            'bag': 'shopping-bag',
            'scooter': 'bike',
            'whatsapp': 'message-circle',
            'leaf': 'leaf',
            'clock': 'timer',
        }.get(self.icon, 'sparkles')

    def __str__(self):
        return self.title_ar


class Testimonial(TimeStampedModel):
    customer_name = models.CharField(max_length=120, verbose_name='اسم العميل')
    review_ar = models.TextField(verbose_name='التقييم بالعربية')
    review_en = models.TextField(blank=True, verbose_name='التقييم بالإنجليزية')
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='عدد النجوم')
    avatar = models.ImageField(upload_to='testimonials/', blank=True, verbose_name='الصورة الشخصية')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'رأي عميل'
        verbose_name_plural = 'آراء العملاء'

    def __str__(self):
        return self.customer_name


class FAQ(TimeStampedModel):
    question_ar = models.CharField(max_length=255, verbose_name='السؤال بالعربية')
    question_en = models.CharField(max_length=255, verbose_name='السؤال بالإنجليزية')
    answer_ar = models.TextField(verbose_name='الإجابة بالعربية')
    answer_en = models.TextField(verbose_name='الإجابة بالإنجليزية')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'سؤال شائع'
        verbose_name_plural = 'الأسئلة الشائعة'

    def __str__(self):
        return self.question_ar


class SocialPost(TimeStampedModel):
    title = models.CharField(max_length=100, blank=True, verbose_name='العنوان الداخلي')
    image = models.ImageField(upload_to='social/', blank=True, verbose_name='الصورة')
    image_url = models.CharField(
        max_length=500,
        blank=True,
        validators=[image_source_validator],
        verbose_name='رابط أو مسار صورة بديل',
    )
    post_url = models.URLField(blank=True, verbose_name='رابط المنشور')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'صورة تواصل اجتماعي'
        verbose_name_plural = 'صور التواصل الاجتماعي'

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.title or f'Social #{self.pk}'


class Reservation(TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('contacted', 'تم التواصل'),
        ('confirmed', 'مؤكد'),
        ('cancelled', 'ملغي'),
    ]
    full_name = models.CharField(max_length=150, verbose_name='الاسم الكامل')
    phone = models.CharField(max_length=40, verbose_name='رقم الهاتف')
    date = models.DateField(verbose_name='التاريخ')
    time = models.TimeField(verbose_name='الوقت')
    guests = models.PositiveSmallIntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(50)], verbose_name='عدد الأشخاص')
    occasion = models.CharField(max_length=120, blank=True, verbose_name='المناسبة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='الحالة')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب حجز'
        verbose_name_plural = 'طلبات الحجز'
        indexes = [
            models.Index(fields=['date', 'time', 'status']),
        ]

    def __str__(self):
        return f'{self.full_name} - {self.date}'


class Order(TimeStampedModel):
    """An order priced by the server.

    The customer's browser only ever sends dish ids and quantities; every
    price here is read from the menu at the moment the order is created, so
    editing the page or the WhatsApp message cannot change what the
    restaurant is owed. The short code is what staff verify against.
    """

    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('confirmed', 'مؤكد'),
        ('preparing', 'قيد التحضير'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
    ]
    FULFILLMENT_CHOICES = [
        ('pickup', 'استلام من المطعم'),
        ('delivery', 'ديليفري'),
        ('dine_in', 'داخل المطعم'),
    ]
    SOURCE_CHOICES = [
        ('online', 'أونلاين'),
        ('cashier', 'داخل المطعم'),
    ]
    # No I, O, 0 or 1: the code gets read aloud over the phone.
    CODE_ALPHABET = 'ACDEFGHJKLMNPQRSTUVWXYZ23456789'
    CODE_LENGTH = 4

    code = models.CharField(max_length=16, unique=True, editable=False, verbose_name='رقم الطلب')
    # The code is short so it can be read aloud, which also makes it easy to
    # guess. The order page shows a customer's name, phone and address, so the
    # URL uses this separate high-entropy token instead.
    token = models.CharField(max_length=32, unique=True, editable=False, verbose_name='مفتاح الرابط')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='الحالة')
    fulfillment = models.CharField(max_length=20, choices=FULFILLMENT_CHOICES, default='pickup', verbose_name='طريقة الاستلام')
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='online',
        verbose_name='مصدر الطلب',
    )

    customer_name = models.CharField(max_length=150, blank=True, verbose_name='اسم العميل')
    customer_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='عدد الزبائن',
    )
    table_number = models.CharField(max_length=30, blank=True, verbose_name='رقم الطاولة')
    phone = models.CharField(max_length=40, blank=True, verbose_name='رقم الجوال')
    address = models.TextField(blank=True, verbose_name='عنوان التوصيل')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cashier_orders',
        verbose_name='الكاشير',
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'), verbose_name='الإجمالي')
    currency = models.CharField(max_length=20, default='₪', verbose_name='العملة')
    has_unpriced_lines = models.BooleanField(default=False, verbose_name='يحتوي عرضًا يُسعّر لاحقًا')

    # Snapshotted so an old receipt still shows the branding it was made with.
    restaurant_name = models.CharField(max_length=120, blank=True, verbose_name='اسم المطعم')
    restaurant_tagline = models.CharField(max_length=160, blank=True, verbose_name='شعار المطعم')

    language = models.CharField(max_length=5, default='ar', verbose_name='لغة الطلب')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['source', '-created_at']),
            models.Index(fields=['phone']),
        ]

    def save(self, *args, **kwargs):
        import secrets

        if not self.code:
            self.code = self._new_code()
        if not self.token:
            self.token = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)

    @classmethod
    def _new_code(cls):
        import secrets

        for _ in range(20):
            body = ''.join(secrets.choice(cls.CODE_ALPHABET) for _ in range(cls.CODE_LENGTH))
            candidate = f'B12-{body}'
            if not cls.objects.filter(code=candidate).exists():
                return candidate
        # Astronomically unlikely; fall back to a longer code rather than fail.
        return f'B12-{secrets.token_hex(4).upper()}'

    @property
    def item_count(self):
        return sum(line.quantity for line in self.lines.all())

    def __str__(self):
        return f'{self.code} — {self.customer_name or "بدون اسم"}'


class OrderLine(TimeStampedModel):
    """One priced line. Names and prices are copies, not references, so a
    later menu edit never rewrites a past order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines', verbose_name='الطلب')
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_lines', verbose_name='الطبق',
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_lines', verbose_name='العرض',
    )
    name_ar = models.CharField(max_length=150, verbose_name='الاسم بالعربية')
    name_en = models.CharField(max_length=150, blank=True, verbose_name='الاسم بالإنجليزية')
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)], verbose_name='الكمية')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'), verbose_name='سعر الوحدة')
    is_priced = models.BooleanField(default=True, verbose_name='له سعر ثابت')
    price_note = models.CharField(max_length=80, blank=True, verbose_name='نص السعر')

    class Meta:
        ordering = ['id']
        verbose_name = 'صنف في الطلب'
        verbose_name_plural = 'أصناف الطلب'

    @property
    def line_total(self):
        return self.unit_price * self.quantity if self.is_priced else Decimal('0')

    def __str__(self):
        return f'{self.name_ar} × {self.quantity}'
