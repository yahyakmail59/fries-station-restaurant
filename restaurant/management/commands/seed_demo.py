from decimal import Decimal

from django.core.management.base import BaseCommand

from restaurant.models import (
    Category,
    FAQ,
    HeroStat,
    MenuItem,
    Offer,
    RestaurantSettings,
    Service,
    SocialPost,
    Testimonial,
)


class Command(BaseCommand):
    help = 'Load the approved B12 landing-page content and generated high-resolution images.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update the demo records even when menu content already exists.',
        )

    def handle(self, *args, **options):
        if Category.objects.exists() and not options['force']:
            self.stdout.write(self.style.WARNING(
                'Menu content already exists; demo seeding was skipped to protect Admin changes. Use --force to reload defaults.'
            ))
            return
        v3 = '/static/restaurant/img/v3'

        site = RestaurantSettings.load()
        site.name_ar = 'مطعم B12'
        site.name_en = 'B12 Restaurant'
        site.tagline_ar = 'الطعم حكاية'
        site.tagline_en = 'Taste Tells a Story'
        site.hero_title_ar = 'الطعم حكاية'
        site.hero_title_en = 'Taste Tells a Story'
        site.hero_text_ar = 'رحلة من النكهات العالمية والشرقية الأصيلة، محضّرة بأجود المكونات وبلمسة استثنائية.'
        site.hero_text_en = 'A journey of global and oriental flavours crafted with premium ingredients and passion.'
        site.hero_image_url = f'{v3}/hero-b12.webp'

        site.about_title_ar = 'من نحن'
        site.about_title_en = 'About Us'
        site.about_text_ar = 'وُلد مطعم B12 من شغف حقيقي بالطعم الأصيل. نجمع بين المشاوي الشرقية والأطباق العالمية في مكان واحد، ونحضّر كل طبق يوميًا بمكونات طازجة مختارة بعناية، لنقدم لكم تجربة تستحق التكرار.'
        site.about_text_en = 'B12 was born from a real passion for authentic flavour. We bring oriental grills and international dishes together under one roof, preparing every dish daily with carefully selected fresh ingredients.'
        site.show_about = True

        site.primary_color = '#D71920'
        site.gold_color = '#FFC107'
        site.deep_color = '#8C1518'
        site.orange_color = '#FF6D00'
        site.background_color = '#F5F5F5'
        site.surface_color = '#FFFFFF'
        site.whatsapp_color = '#25D366'

        site.menu_title_ar = 'استكشف أقسام القائمة'
        site.menu_title_en = 'Explore Our Menu'
        site.featured_title_ar = 'أطباق مميزة'
        site.featured_title_en = 'Featured Menu'
        site.offers_title_ar = 'عروض وأطباق مميزة'
        site.offers_title_en = 'Special Offers'
        site.services_title_ar = 'خدماتنا'
        site.services_title_en = 'Our Services'
        site.reviews_title_ar = 'آراء عملائنا'
        site.reviews_title_en = 'Customer Reviews'
        site.reservation_title_ar = 'احجز طاولتك أو تواصل معنا'
        site.reservation_title_en = 'Reservation & Contact'
        site.reservation_text_ar = 'احجز طاولتك بسهولة أو تواصل معنا مباشرة عبر واتساب.'
        site.reservation_text_en = 'Reserve your table easily or contact us directly on WhatsApp.'
        site.faq_title_ar = 'الأسئلة الشائعة'
        site.faq_title_en = 'FAQ'
        site.social_title_ar = 'تابعنا على إنستغرام'
        site.social_title_en = 'Follow Us on Instagram'

        site.order_cta_ar = 'اطلب الآن عبر واتساب'
        site.order_cta_en = 'Order on WhatsApp'
        site.menu_cta_ar = 'استعرض القائمة'
        site.menu_cta_en = 'View Menu'
        site.whatsapp_panel_text_ar = 'خدمة سريعة، رد فوري، وطلب سهل.'
        site.whatsapp_panel_text_en = 'Fast service, quick reply and an easy order.'
        site.seo_title_ar = 'مطعم B12 | الطعم حكاية'
        site.seo_title_en = 'B12 Restaurant | Taste Tells a Story'
        site.seo_description_ar = 'قائمة متنوعة من المشاوي والبرجر والباستا والبيتزا والمشروبات مع إمكانية الطلب مباشرة عبر واتساب.'
        site.seo_description_en = 'Grills, burgers, pasta, pizza and drinks with direct WhatsApp ordering.'
        site.footer_text_ar = 'رحلة من النكهات العالمية والشرقية الأصلية، مع جودة فاخرة وتجربة لا تُنسى.'
        site.footer_text_en = 'Authentic global and oriental flavours with premium quality and an unforgettable experience.'

        site.whatsapp_number = '972597862389'
        site.phone = '+972 59 786 2389'
        site.email = 'info@b12restaurant.com'
        site.address_ar = 'غرب غزة - دوار حيدر'
        site.address_en = 'West Gaza - Haidar Roundabout'
        site.hours_ar = 'يوميًا من 8 صباحًا حتى 2 صباحًا'
        site.hours_en = 'Daily, 8:00 AM - 2:00 AM'
        site.currency = '₪'
        site.show_categories = True
        site.show_featured = True
        site.show_offers = True
        site.show_services = True
        site.show_reviews = True
        site.show_reservation = True
        site.show_faq = True
        site.show_social = True
        site.save()

        stats = [
            ('مكونات طازجة يوميًا', 'Fresh Ingredients', 'leaf', 1),
            ('خدمة سريعة', 'Fast Service', 'clock', 2),
            ('جودة فاخرة', 'Premium Quality', 'crown', 3),
        ]
        for title_ar, title_en, icon, order in stats:
            HeroStat.objects.update_or_create(
                title_en=title_en,
                defaults={
                    'title_ar': title_ar,
                    'icon': icon,
                    'display_order': order,
                    'is_active': True,
                },
            )

        category_data = [
            ('شرقي', 'Eastern', 'eastern', 'skewer', 'mixed-grill-960.webp', 1),
            ('غربي', 'Western', 'western', 'burger', 'burger-960.webp', 2),
            ('إيطالي', 'Italian', 'italian', 'pasta', 'pasta-960.webp', 3),
            ('بيتزا', 'Pizza', 'pizza', 'pizza', 'pizza-960.webp', 4),
            ('مشروبات', 'Drinks', 'drinks', 'drink', 'drinks-960.webp', 5),
            ('حلويات', 'Desserts', 'desserts', 'dessert', 'dessert-960.webp', 6),
        ]
        categories = {}
        for name_ar, name_en, slug, icon, image_name, order in category_data:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_ar': name_ar,
                    'name_en': name_en,
                    'icon': icon,
                    'image_url': f'{v3}/{image_name}',
                    'display_order': order,
                    'is_active': True,
                },
            )
            categories[slug] = category

        items = [
            (
                'eastern', 'كباب مشوي مشكل', 'Mixed Grilled Kebab',
                'تشكيلة مشاوي شرقية متبلة بعناية، تقدم مع البطاطا والخضار المشوية.',
                'Carefully seasoned oriental mixed grill with fries and grilled vegetables.',
                '75.00', 'mixed-grill-960.webp', 1,
            ),
            (
                'western', 'ستيك ريب آي', 'Ribeye Steak',
                'ستيك بقري طري مشوي على اللهب مع الأعشاب والطماطم المشوية.',
                'Flame-grilled tender ribeye with herbs and roasted tomatoes.',
                '89.00', 'steak-960.webp', 2,
            ),
            (
                'italian', 'باستا ألفريدو', 'Pasta Alfredo',
                'باستا كريمية غنية بجبنة البارميزان ولمسة من الأعشاب الإيطالية.',
                'Rich creamy pasta with parmesan and a touch of Italian herbs.',
                '58.00', 'pasta-960.webp', 3,
            ),
            (
                'pizza', 'بيتزا بيبروني', 'Pepperoni Pizza',
                'عجينة طازجة، صلصة طماطم إيطالية، موزاريلا وشرائح بيبروني.',
                'Fresh dough, Italian tomato sauce, mozzarella and pepperoni.',
                '52.00', 'pizza-960.webp', 4,
            ),
            (
                'eastern', 'شاورما دجاج', 'Chicken Shawarma',
                'شاورما دجاج ساخنة مع الثوم والمخللات والبطاطا والخبز الطازج.',
                'Hot chicken shawarma with garlic sauce, pickles, fries and fresh bread.',
                '32.00', 'shawarma-960.webp', 5,
            ),
            (
                'western', 'برجر B12 المميز', 'B12 Signature Burger',
                'قطعتان من اللحم، جبنة شيدر، خضار طازجة وصوص B12 الخاص.',
                'Double beef, cheddar, fresh vegetables and signature B12 sauce.',
                '48.00', 'burger-960.webp', 6,
            ),
            (
                'eastern', 'سمك فيليه مشوي', 'Grilled Fish Fillet',
                'فيليه سمك متبل ومشوي يقدم مع الليمون والطماطم والأعشاب.',
                'Seasoned grilled fish fillet with lemon, tomatoes and herbs.',
                '69.00', 'fish-960.webp', 7,
            ),
            (
                'drinks', 'موهيتو التوت', 'Berry Mojito',
                'مزيج منعش من التوت والليمون والنعناع الطازج والثلج.',
                'A refreshing blend of berries, lime, fresh mint and ice.',
                '22.00', 'drinks-960.webp', 8,
            ),
        ]
        for category_slug, name_ar, name_en, description_ar, description_en, price, image_name, order in items:
            MenuItem.objects.update_or_create(
                name_en=name_en,
                defaults={
                    'category': categories[category_slug],
                    'name_ar': name_ar,
                    'description_ar': description_ar,
                    'description_en': description_en,
                    'price': Decimal(price),
                    'old_price': None,
                    'image_url': f'{v3}/{image_name}',
                    'is_featured': True,
                    'is_available': True,
                    'display_order': order,
                },
            )

        offers = [
            (
                'عرض الجمعة', 'Friday Grill Offer',
                'خصم على تشكيلة المشاوي المختارة كل يوم جمعة.',
                'A special discount on selected grills every Friday.',
                'خصم 30%', '30% OFF', 'mixed-grill-960.webp', 1,
            ),
            (
                'برجر B12 سبيشل', 'B12 Special Burger',
                'برجر B12 المميز مع البطاطا والمشروب بسعر خاص.',
                'B12 signature burger with fries and a drink.',
                '35 ₪', '35 ILS', 'burger-960.webp', 2,
            ),
            (
                'عرض العائلة', 'Family Deal',
                'بيتزا كبيرة، مشاوي مشكلة، مشروبات وحلوى للمشاركة.',
                'Large pizza, mixed grill, drinks and dessert for sharing.',
                '199 ₪', '199 ILS', 'hero-b12-960.webp', 3,
            ),
        ]
        for title_ar, title_en, desc_ar, desc_en, price_ar, price_en, image_name, order in offers:
            Offer.objects.update_or_create(
                title_en=title_en,
                defaults={
                    'title_ar': title_ar,
                    'description_ar': desc_ar,
                    'description_en': desc_en,
                    'price_text_ar': price_ar,
                    'price_text_en': price_en,
                    'image_url': f'{v3}/{image_name}',
                    'display_order': order,
                    'is_active': True,
                },
            )

        services = [
            ('تناول في المطعم', 'Dine-in Experience', 'أجواء هادئة وجلسات مريحة وخدمة راقية.', 'Comfortable seating and an elegant atmosphere.', 'dine', 1),
            ('طلبات خارجية', 'Takeaway', 'استلام سريع ومنظم من المطعم.', 'Fast and organised pickup.', 'bag', 2),
            ('توصيل سريع', 'Fast Delivery', 'تجهيز سريع والتوصيل حسب المنطقة.', 'Fast preparation and area-based delivery.', 'scooter', 3),
            ('اطلب عبر واتساب', 'WhatsApp Order', 'أضف أطباقك وأرسل طلبًا مرتبًا خلال ثوانٍ.', 'Build and send your order in seconds.', 'whatsapp', 4),
            ('مكونات فاخرة', 'Premium Ingredients', 'مكونات مختارة بعناية وتحضير يومي.', 'Carefully selected, freshly prepared ingredients.', 'leaf', 5),
            ('تحضير سريع', 'Fast Preparation', 'سرعة لا تؤثر على الجودة والطعم.', 'Fast service without compromising quality.', 'clock', 6),
        ]
        for title_ar, title_en, desc_ar, desc_en, icon, order in services:
            Service.objects.update_or_create(
                title_en=title_en,
                defaults={
                    'title_ar': title_ar,
                    'description_ar': desc_ar,
                    'description_en': desc_en,
                    'icon': icon,
                    'display_order': order,
                    'is_active': True,
                },
            )

        reviews = [
            ('أحمد العتيبي', 'أروع المطاعم من ناحية الأكل اللذيذ والخدمة الممتازة والأجواء الراقية جدًا.', 'Amazing food, excellent service and a very elegant atmosphere.', 5, 1),
            ('Sarah M.', 'الأطباق شهية والخدمة سريعة والمكان مريح. سأكرر الزيارة بالتأكيد.', 'Delicious dishes, fast service and a comfortable place. I will visit again.', 5, 2),
            ('محمد الزهراني', 'طلبت عبر واتساب وكان الطلب مرتبًا وسهلًا ووصل الطعام ساخنًا.', 'The WhatsApp order was easy and the food arrived hot and well packed.', 5, 3),
        ]
        for name, review_ar, review_en, rating, order in reviews:
            Testimonial.objects.update_or_create(
                customer_name=name,
                defaults={
                    'review_ar': review_ar,
                    'review_en': review_en,
                    'rating': rating,
                    'display_order': order,
                    'is_active': True,
                },
            )

        faq_data = [
            ('هل جميع الأطباق حلال؟', 'Are all dishes halal?', 'نعم، جميع اللحوم والمكونات المستخدمة حلال.', 'Yes, all meats and ingredients used are halal.', 1),
            ('هل يمكنني تعديل الطلب؟', 'Can I customise my order?', 'نعم، أضف ملاحظاتك قبل إرسال الطلب عبر واتساب.', 'Yes. Add your notes before sending the WhatsApp order.', 2),
            ('هل لديكم أطباق نباتية؟', 'Do you offer vegetarian dishes?', 'تتوفر خيارات نباتية ويمكن الاستفسار عنها عبر واتساب.', 'Vegetarian choices are available; ask us on WhatsApp.', 3),
            ('ما هي مناطق التوصيل؟', 'Which areas do you deliver to?', 'تختلف التغطية والتكلفة حسب المنطقة ويتم تأكيدهما عبر واتساب.', 'Coverage and fees vary by area and are confirmed on WhatsApp.', 4),
            ('كيف يمكنني الطلب؟', 'How can I order?', 'أضف الأطباق إلى طلبك ثم أرسله مباشرة عبر واتساب.', 'Add dishes to your cart and send the order directly on WhatsApp.', 5),
            ('ما هي طرق الدفع المتاحة؟', 'Which payment methods are available?', 'يتم تأكيد طريقة الدفع المناسبة عند التواصل عبر واتساب.', 'The suitable payment method is confirmed through WhatsApp.', 6),
        ]
        for question_ar, question_en, answer_ar, answer_en, order in faq_data:
            FAQ.objects.update_or_create(
                question_en=question_en,
                defaults={
                    'question_ar': question_ar,
                    'answer_ar': answer_ar,
                    'answer_en': answer_en,
                    'display_order': order,
                    'is_active': True,
                },
            )

        social_images = [
            ('برجر B12', 'burger-960.webp', 1),
            ('باستا ألفريدو', 'pasta-960.webp', 2),
            ('مشاوي B12', 'mixed-grill-960.webp', 3),
            ('بيتزا بيبروني', 'pizza-960.webp', 4),
            ('مشروبات منعشة', 'drinks-960.webp', 5),
            ('حلوى الشوكولاتة', 'dessert-960.webp', 6),
        ]
        for title, image_name, order in social_images:
            SocialPost.objects.update_or_create(
                title=title,
                defaults={
                    'image_url': f'{v3}/{image_name}',
                    'display_order': order,
                    'is_active': True,
                },
            )

        self.stdout.write(self.style.SUCCESS('B12 V3 content and high-resolution generated images loaded successfully.'))
