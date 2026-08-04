"""Load the verified Fries Station menu.

Every name, price and ingredient list here was taken from the restaurant's
own live ordering page and its printed menu. Nothing is invented: an item
with no confirmed photograph is loaded without one rather than given a
stand-in, and no allergen or health claim is asserted anywhere, because the
source states none.

Where the printed menu and the live page disagree, the live page wins — it
is what the restaurant charges today. The differences are listed in
docs/menu-source.md.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import (
    Category,
    FAQ,
    HeroStat,
    MenuItem,
    MenuItemSize,
    RestaurantSettings,
    Service,
)

IMG = '/static/restaurant/img/fries-station'

CATEGORIES = [
    # slug, ar, en, icon, cover, order
    ('fries', 'فرايز', 'Fries Meals', 'fries', 'fries', 1),
    ('stripes', 'ستربس', 'Stripes Meals', 'chicken', 'stripes', 2),
    ('sandwiches', 'ساندويتشات وبرجر', 'Sandwiches & Burgers', 'burger', 'sandwiches', 3),
    ('kids', 'وجبات الأطفال', 'Kids Meal', 'kids', 'kids', 4),
    ('sauces', 'صوصات', 'Sauces', 'sauce', 'sauces', 5),
    ('salad', 'سلطات', 'Salad', 'salad', 'salad', 6),
    ('sweets', 'حلويات', 'Sweets', 'dessert', 'sweets', 7),
    ('drinks', 'مشروبات', 'Drinks', 'drink', 'drinks', 8),
    ('extras', 'إضافات', 'Extras', 'sauce', 'sauces', 9),
]

# slug, category, ar, en, price, description_ar, description_en, has_photo, featured
ITEMS = [
    ('fries', 'fries', 'فرايز', 'Fries', '7.00', '', '', True, False),
    ('boom-fries', 'fries', 'بوم فرايز', 'Boom Fries', '45.00',
     'فرايز - قطع ستربس - سماش برجر - صوصات - مكس جبن - هاليبينو',
     'Fries, chicken stripes, smash burger, sauces, cheese mix, jalapeño',
     True, True),
    ('smash-fries', 'fries', 'سماش فرايز', 'Smash Fries', '40.00',
     'فرايز - دبل سماش برجر - صوصات - مكس جبن - هاليبينو - مخلل',
     'Fries, double smash burger, sauces, cheese mix, jalapeño, pickles',
     True, True),
    ('zinger-fries', 'fries', 'زنجر فرايز', 'Zinger Fries', '37.00',
     'فرايز - دبل ستربس - صوصات - مكس جبن - هاليبينو - مخلل',
     'Fries, double chicken stripes, sauces, cheese mix, jalapeño, pickles',
     True, True),
    ('piccata-fries', 'fries', 'بيكاتا فرايز', 'Piccata Fries', '40.00',
     'فرايز - صدر دجاج - فلفل ألوان - مشروم - ثوم وليمون - ذرة',
     'Fries, chicken breast, bell peppers, mushroom, garlic and lemon, corn',
     True, False),
    ('nuggets-fries', 'fries', 'ناجيتس فرايز', 'Nuggets Fries', '37.00',
     'فرايز - سلايز بانيه - صوص سكالوبيني - مكس جبن - زيتون أسود',
     'Fries, breaded chicken slices, scaloppine sauce, cheese mix, black olives',
     True, False),
    ('shrimp-fries', 'fries', 'شريمب فرايز', 'Shrimp Fries', '42.00',
     'فرايز - 7 قطع جمبري بانيه - صوص فرايد شريمب - صوص هوت هني',
     'Fries, 7 breaded shrimp, fried shrimp sauce, hot honey sauce',
     True, True),
    ('royal-fries', 'fries', 'رويال فرايز', 'Royal Fries', '40.00',
     'فرايز ودجز - قطع صدر دجاج - خس - صوص - بندورة',
     'Wedge fries, chicken breast pieces, lettuce, sauce, tomato',
     True, False),
    ('classic-fries', 'fries', 'كلاسيك فرايز', 'Classic Fries', '25.00',
     'فرايز - مكس صوصات - مكس جبن',
     'Fries, mixed sauces, cheese mix',
     True, False),
    ('shrimp-cut-fries', 'fries', 'جمبري فرايز', 'Jumbo Fries', '25.00',
     'جمبري فرايز - مكس صوصات - مكس جبن',
     'Jumbo-cut fries, mixed sauces, cheese mix',
     True, False),

    ('gold-stripes', 'stripes', 'جولد ستربس', 'Gold Stripes', '40.00',
     '4 قطع ستربس - فرايز - خبز برجر - كول سلو - صوص',
     '4 chicken stripes, fries, burger bun, coleslaw, sauce',
     True, True),
    ('fire-stripes', 'stripes', 'فاير ستربس', 'Fire Stripes', '43.00',
     '4 قطع ستربس بصوص الهوت هني الحار - فرايز - خبز برجر - كول سلو - صوص',
     '4 chicken stripes in spicy hot honey sauce, fries, burger bun, coleslaw, sauce',
     True, False),
    ('buffalo-stripes', 'stripes', 'بافلو ستربس', 'Buffalo Stripes', '43.00',
     '4 قطع ستربس بصوص البافلو الحار - فرايز - خبز برجر - كول سلو - صوص',
     '4 chicken stripes in spicy buffalo sauce, fries, burger bun, coleslaw, sauce',
     True, False),

    ('kids-meal', 'kids', 'وجبة أطفال', 'Kids Meal', '30.00',
     '"مايتي زنجر" خبز برجر - خس - بندورة - صوص شيدر - عصير - هدية أطفال',
     'Mighty Zinger burger bun, lettuce, tomato, cheddar sauce, juice, a small gift',
     True, False),

    ('smoky-station-bbq', 'sandwiches', 'سموكي ستيشن BBQ', 'Smoky Station BBQ', '40.00',
     'خبز تورتيلا - صوص ماك سموك - فرايز - صدر دجاج مدخن - هاليبينو - مكس جبن',
     'Tortilla wrap, mac smoke sauce, fries, smoked chicken breast, jalapeño, cheese mix',
     True, False),
    ('crunch-fries', 'sandwiches', 'كرنوش فرايز', 'Crunch Fries Wrap', '45.00',
     'خبز تورتيلا - صوص FS المميز - فرايز - دبل ستربس - خس - هاليبينو - مكس جبن',
     'Tortilla wrap, signature FS sauce, fries, double chicken stripes, lettuce, jalapeño, cheese mix',
     True, True),
    ('smash-burger', 'sandwiches', 'سماش برجر', 'Smash Burger', '40.00',
     'خبز برجر - صوص FS المميز - خس - بندورة - مخلل خيار - دبل سماش برجر - صوص شيدر - فرايز',
     'Burger bun, signature FS sauce, lettuce, tomato, pickles, double smash patty, cheddar sauce, fries',
     True, True),
    ('pop-zinger', 'sandwiches', 'بوب زنجر', 'Pop Zinger', '35.00',
     'خبز برجر - كول سلو - صدر دجاج مقرمش - خس - بندورة - مخلل خيار - صوص شيدر - فرايز',
     'Burger bun, coleslaw, crispy chicken breast, lettuce, tomato, pickles, cheddar sauce, fries',
     True, False),
    ('chicken-piccata', 'sandwiches', 'تشيكن بيكاتا', 'Chicken Piccata', '38.00',
     'شرائح صدر الدجاج - فلفل ألوان - ثوم - شرائح بصل - ليمون - مشروم - فرايز',
     'Sliced chicken breast, bell peppers, garlic, sliced onion, lemon, mushroom, fries',
     True, False),
    ('hammer-station', 'sandwiches', 'هامر ستيشن', 'Hammer Station', '50.00',
     'فينو جامبو - ستيك صدر مقرمش - صوص FS المميز - شرائح بندورة - صوص شيدر - هاليبينو - مكس جبن - فرايز',
     'Jumbo baguette, crispy chicken steak, signature FS sauce, sliced tomato, cheddar sauce, jalapeño, cheese mix, fries',
     True, True),

    ('fs-sauce', 'sauces', 'صوص FS', 'FS Sauce', '4.00', '', '', True, False),
    ('cheddar-sauce', 'sauces', 'شيدر صوص', 'Cheddar Sauce', '4.00', '', '', True, False),
    ('ranch-sauce', 'sauces', 'رانش صوص', 'Ranch Sauce', '4.00', '', '', True, False),
    ('buffalo-sauce', 'sauces', 'بافلو صوص', 'Buffalo Sauce', '4.00', '', '', True, False),
    ('bbq-sauce', 'sauces', 'باربيكيو صوص', 'BBQ Sauce', '4.00', '', '', True, False),
    ('piccante-sauce', 'sauces', 'بيكانتي صوص', 'Piccante Sauce', '4.00', '', '', True, False),
    ('dynamite-sauce', 'sauces', 'ديناميت صوص', 'Dynamite Sauce', '4.00', '', '', True, False),
    ('hot-honey-sauce', 'sauces', 'هوت هني صوص', 'Hot Honey Sauce', '4.00', '', '', True, False),
    ('garlic-cream-sauce', 'sauces', 'كريم ثوم صوص', 'Garlic Cream Sauce', '4.00', '', '', True, False),
    ('mac-smoke-sauce', 'sauces', 'ماك سموك صوص', 'Mac Smoke Sauce', '4.00', '', '', True, False),
    ('creamy-ketch-sauce', 'sauces', 'كريمي كاتش صوص', 'Creamy Ketch Sauce', '4.00', '', '', True, False),

    ('coleslaw', 'salad', 'كول سلو', 'Coleslaw', '5.00', '', '', True, False),
    ('corn-mayo', 'salad', 'ذرة بالمايونيز', 'Corn with Mayo', '5.00', '', '', True, False),

    ('churros-classic', 'sweets', 'تشيروز كلاسيك', 'Classic Churros', '10.00', '', '', True, False),
    ('churros-sauces', 'sweets', 'تشيروز بالصوصات', 'Churros with Sauces', '15.00',
     'بستاشيو .. أوريو .. كراميل .. نوتيلا',
     'Pistachio, Oreo, caramel or Nutella',
     True, True),

    ('seasonal-juice', 'drinks', 'عصير الموسم', 'Seasonal Juice', '15.00', '', '', True, False),
    ('coca-cola', 'drinks', 'كوكاكولا', 'Coca-Cola', '5.00', '', '', True, False),
    ('sprite', 'drinks', 'سبرايت', 'Sprite', '5.00', '', '', True, False),
    ('water', 'drinks', 'مياه', 'Water 500ml', '5.00', '500 مل', '500 ml', True, False),

    ('vienna-bread', 'extras', 'فينو', 'Vienna Bread', '2.00', '', '', True, False),
]

# Sizes exactly as the restaurant's own ordering system stores them: absolute
# prices, not surcharges. Small first, so the card's "from" price is the small.
SIZES = {
    'fries': [('صغير', 'Small', '7.00'), ('كبير', 'Large', '15.00')],
    'coleslaw': [('صغير', 'Small', '5.00'), ('كبير', 'Large', '8.00')],
    'corn-mayo': [('صغير', 'Small', '5.00'), ('كبير', 'Large', '8.00')],
}
# All eleven sauces share one pair.
for _sauce in (
    'fs-sauce', 'cheddar-sauce', 'ranch-sauce', 'buffalo-sauce', 'bbq-sauce',
    'piccante-sauce', 'dynamite-sauce', 'hot-honey-sauce', 'garlic-cream-sauce',
    'mac-smoke-sauce', 'creamy-ketch-sauce',
):
    SIZES[_sauce] = [('صغير', 'Small', '4.00'), ('كبير', 'Large', '7.00')]

HERO_STATS = [
    ('تُقلى عند الطلب', 'Fried to order', 'clock'),
    ('صوصاتنا الخاصة', 'Our own sauces', 'leaf'),
    ('١١ صوصًا للاختيار', '11 sauces to choose', 'star'),
]

SERVICES = [
    ('استلام من الفرع', 'Pickup', 'اطلب واستلم طلبك جاهزًا.', 'Order ahead and collect it ready.', 'bag'),
    ('توصيل', 'Delivery', 'نوصل طلبك إليك ساخنًا.', 'We bring your order to you hot.', 'scooter'),
    ('تناول في المطعم', 'Dine in', 'اجلس عندنا واطلب من الكاشير.', 'Sit with us and order at the counter.', 'dine'),
    ('طلب عبر واتساب', 'Order on WhatsApp', 'أرسل طلبك برسالة واحدة.', 'Send your order in one message.', 'whatsapp'),
]

FAQS = [
    ('ما ساعات العمل؟', 'What are your opening hours?',
     'يوميًا من 11:30 صباحًا حتى 11:30 مساءً.',
     'Daily from 11:30 AM to 11:30 PM.'),
    ('هل الطلب أونلاين متاح؟', 'Can I order online?',
     'نعم، أضف ما تريد إلى السلة وأرسل الطلب عبر واتساب، وسيصلك رقم الطلب فورًا.',
     'Yes. Add what you want to the cart and send the order on WhatsApp; you get an order number straight away.'),
    ('كم عدد الصوصات المتاحة؟', 'How many sauces do you have?',
     'أحد عشر صوصًا، منها صوص FS المميز والهوت هني والديناميت.',
     'Eleven, including our signature FS sauce, hot honey and dynamite.'),
    ('هل توجد وجبة للأطفال؟', 'Do you have a kids meal?',
     'نعم، وجبة أطفال تشمل مايتي زنجر وعصيرًا وهدية.',
     'Yes — a kids meal with a Mighty Zinger, a juice and a small gift.'),
]


class Command(BaseCommand):
    help = 'Load the verified Fries Station categories, menu items and site content.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing menu content. Refuses to run without it once a menu exists.',
        )

    def handle(self, *args, **options):
        if Category.objects.exists() and not options['force']:
            self.stdout.write(self.style.WARNING(
                'A menu already exists; nothing was changed. Pass --force to reload it, '
                'but never against a database that is taking real orders.'
            ))
            return

        site = RestaurantSettings.load()
        site.hero_image_url = f'{IMG}/hero/hero-fries-station.webp'
        site.og_image_url = f'{IMG}/branding/og-fries-station.webp'
        # The restaurant's own public pages, confirmed by the owner.
        # Contact details as the restaurant publishes them on its own pages.
        site.facebook_url = 'https://www.facebook.com/FriesStation.Rest/'
        site.instagram_url = 'https://www.instagram.com/friesstation.rest/'
        site.tiktok_url = 'https://www.tiktok.com/@friesstation.rest'
        site.phone = '+970 593 388 855'
        site.email = 'info@friesstation.rest'
        site.address_ar = 'غزة - شارع الوحدة - غرب مفترق العائلات'
        site.address_en = 'Gaza - Al-Wehda Street - west of Al-Ailat junction'
        site.tagline_ar = 'مقرمشة. تُقلى عند الطلب.'
        site.tagline_en = 'Crispy. Fried to order.'
        site.hero_title_ar = 'فرايز مقرمشة تُقلى عند الطلب'
        site.hero_title_en = 'Fried to order. Your way.'
        site.hero_text_ar = 'اختر وجبتك وحجمك، راجع السعر، ثم أرسل طلبك جاهزًا عبر واتساب. متاح للاستلام أو التوصيل.'
        site.hero_text_en = 'Choose your meal and size, review the price, then send your ready order on WhatsApp. Pickup and delivery are available.'
        site.menu_title_ar = 'اختر قسمك المفضل'
        site.menu_title_en = 'Choose a Menu Category'
        site.featured_title_ar = 'اختيارات فرايز ستيشن'
        site.featured_title_en = 'Fries Station Picks'
        site.order_cta_ar = 'ابدأ طلبك'
        site.order_cta_en = 'Start your order'
        site.menu_cta_ar = 'شاهد المنيو والأسعار'
        site.menu_cta_en = 'See menu & prices'
        site.whatsapp_panel_text_ar = 'راجع الأصناف والمجموع، ثم أرسل طلبك برسالة واتساب واحدة.'
        site.whatsapp_panel_text_en = 'Review your items and total, then send the order in one WhatsApp message.'
        site.about_text_ar = (
            'أول مطعم متخصص في البطاطا المقلية في فلسطين. نقلي الطلب عند طلبه، '
            'ونصنع صوصاتنا بأنفسنا، ونقدّمها بسرعة وبنفس الجودة في كل مرة.'
        )
        site.about_text_en = (
            'The first restaurant in Palestine dedicated to fries. Everything is '
            'fried to order, the sauces are our own, and the quality is the same '
            'every time.'
        )
        # A stand-in so ordering can be exercised without messaging the
        # restaurant. Replace it under Settings before taking a real order.
        if not site.whatsapp_number:
            site.whatsapp_number = '972597862389'
        site.save()

        for slug, name_ar, name_en, icon, cover, order in CATEGORIES:
            Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_ar': name_ar,
                    'name_en': name_en,
                    'icon': icon,
                    'image_url': f'{IMG}/categories/{cover}.webp',
                    'display_order': order,
                    'is_active': True,
                },
            )

        categories = {c.slug: c for c in Category.objects.all()}
        without_photo = []
        for order, row in enumerate(ITEMS, start=1):
            slug, cat, name_ar, name_en, price, desc_ar, desc_en, has_photo, featured = row
            if not has_photo:
                without_photo.append(name_ar)
            item, _ = MenuItem.objects.update_or_create(
                name_ar=name_ar,
                category=categories[cat],
                defaults={
                    'name_en': name_en,
                    'description_ar': desc_ar,
                    'description_en': desc_en,
                    # With sizes this is the smallest one, which is what the
                    # card advertises. The order is priced from the size row.
                    'price': Decimal(price),
                    # An item whose only available picture is the logo is loaded
                    # without one. A logo standing in for a dish tells the
                    # customer nothing about what arrives.
                    'image_url': f'{IMG}/menu/{slug}.webp' if has_photo else '',
                    'is_featured': featured,
                    'is_available': True,
                    'display_order': order,
                },
            )
            wanted = SIZES.get(slug, [])
            item.sizes.exclude(name_ar__in=[name for name, _, _ in wanted]).delete()
            for size_order, (size_ar, size_en, size_price) in enumerate(wanted, start=1):
                MenuItemSize.objects.update_or_create(
                    menu_item=item,
                    name_ar=size_ar,
                    defaults={
                        'name_en': size_en,
                        'price': Decimal(size_price),
                        'display_order': size_order,
                        'is_available': True,
                    },
                )

        for order, (ar, en, icon) in enumerate(HERO_STATS, start=1):
            HeroStat.objects.update_or_create(
                title_ar=ar,
                defaults={'title_en': en, 'icon': icon, 'display_order': order, 'is_active': True},
            )

        for order, (ar, en, desc_ar, desc_en, icon) in enumerate(SERVICES, start=1):
            Service.objects.update_or_create(
                title_ar=ar,
                defaults={
                    'title_en': en, 'description_ar': desc_ar, 'description_en': desc_en,
                    'icon': icon, 'display_order': order, 'is_active': True,
                },
            )

        for order, (q_ar, q_en, a_ar, a_en) in enumerate(FAQS, start=1):
            FAQ.objects.update_or_create(
                question_ar=q_ar,
                defaults={
                    'question_en': q_en, 'answer_ar': a_ar, 'answer_en': a_en,
                    'display_order': order, 'is_active': True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {Category.objects.count()} categories, {MenuItem.objects.count()} items '
            f'and {MenuItemSize.objects.count()} sizes across '
            f'{MenuItem.objects.filter(sizes__isnull=False).distinct().count()} items.'
        ))
        if without_photo:
            self.stdout.write(self.style.WARNING(
                'No confirmed photograph, loaded without an image: ' + '، '.join(without_photo)
            ))
        if not site.whatsapp_number:
            self.stdout.write(self.style.WARNING(
                'No WhatsApp number is set. Ordering and reservations stay disabled until '
                'one is entered under Settings.'
            ))
