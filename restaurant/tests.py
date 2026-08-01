from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import Permission, User
from django.core.cache import cache
from django.forms import modelform_factory
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import crm
from .models import (
    Category, HeroStat, MenuItem, Offer, Order, OrderLine, Reservation, RestaurantSettings,
    SocialPost,
)


class LandingPageTests(TestCase):
    def setUp(self):
        cache.clear()
        site = RestaurantSettings.load()
        site.whatsapp_number = '972597862389'
        site.save()

    def test_home_page_loads(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'B12')
        self.assertContains(response, 'واتساب')
        self.assertContains(response, 'value="pickup"')
        self.assertContains(response, 'value="delivery"')
        self.assertContains(response, 'id="order-phone"')
        self.assertContains(response, 'id="order-address"')
        self.assertNotContains(response, 'class="footer-order"')
        self.assertContains(response, 'id="clear-cart"')
        self.assertContains(response, 'class="category-card mobile-all-category active"')
        self.assertContains(response, 'id="active-filter-label"')
        self.assertNotContains(response, 'href="#"')

    def test_offers_have_order_buttons(self):
        Offer.objects.create(
            title_ar='عرض اختبار',
            title_en='Test Offer',
            price_text_ar='35 ₪',
            price_text_en='35 ILS',
        )
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'data-id="offer-')
        self.assertContains(response, 'data-offer="true"')
        self.assertContains(response, 'اطلب العرض')

    def test_language_switch_is_saved_in_session(self):
        response = self.client.get(f"{reverse('restaurant:home')}?lang=en")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['site_language'], 'en')
        self.assertContains(response, 'Order on WhatsApp')

    def test_page_direction_matches_the_selected_language(self):
        arabic_home = self.client.get(f"{reverse('restaurant:home')}?lang=ar")
        self.assertContains(arabic_home, '<html lang="ar" dir="rtl">')

        english_home = self.client.get(f"{reverse('restaurant:home')}?lang=en")
        self.assertContains(english_home, '<html lang="en" dir="ltr">')

        arabic_menu = self.client.get(f"{reverse('restaurant:menu')}?lang=ar")
        self.assertContains(arabic_menu, '<html lang="ar" dir="rtl">')

        english_menu = self.client.get(f"{reverse('restaurant:menu')}?lang=en")
        self.assertContains(english_menu, '<html lang="en" dir="ltr">')

    def test_phone_links_strip_invisible_direction_controls(self):
        site = RestaurantSettings.load()
        site.phone = '+970598165873\u2069'
        site.save()

        response = self.client.get(reverse('restaurant:home'))

        self.assertContains(response, 'href="tel:+970598165873"')
        self.assertNotContains(response, '\u2069')

    def test_valid_reservation_is_saved_and_redirects_to_whatsapp(self):
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Test Guest',
                'phone': '+970000000000',
                'date': (date.today() + timedelta(days=1)).isoformat(),
                'time': time(19, 30).strftime('%H:%M'),
                'guests': 4,
                'occasion': 'Birthday',
                'notes': 'Window seat',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('https://wa.me/972597862389'))
        self.assertEqual(Reservation.objects.count(), 1)

    def test_invalid_reservation_is_not_saved(self):
        response = self.client.post(reverse('restaurant:create_reservation'), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'يرجى مراجعة بيانات الحجز')
        self.assertContains(response, 'id="contact"')
        self.assertEqual(response.redirect_chain[-1][0], '/?lang=ar#contact')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_past_reservation_is_rejected_and_values_are_preserved(self):
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Past Guest',
                'phone': '+970000000000',
                'date': (date.today() - timedelta(days=1)).isoformat(),
                'time': '19:30',
                'guests': 2,
            }, follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Past Guest')
        self.assertContains(response, 'لا يمكن الحجز في تاريخ سابق')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_reservation_is_not_saved_without_whatsapp_number(self):
        site = RestaurantSettings.load()
        site.whatsapp_number = ''
        site.save()
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Test Guest',
                'phone': '+970000000000',
                'date': (date.today() + timedelta(days=1)).isoformat(),
                'time': '19:30',
                'guests': 2,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_non_featured_items_are_available_to_category_filter(self):
        category = Category.objects.create(name_ar='حلويات', name_en='Desserts')
        MenuItem.objects.create(
            category=category,
            name_ar='كعكة',
            name_en='Cake',
            price='12.00',
            is_featured=False,
            is_available=True,
        )
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'data-category="desserts"')
        self.assertContains(response, 'كعكة')
        self.assertContains(response, 'data-price="12.00"')
        self.assertContains(response, 'data-lucide="shopping-cart"')

    def test_english_page_uses_english_menu_content(self):
        category = Category.objects.create(name_ar='حلويات', name_en='Desserts')
        MenuItem.objects.create(
            category=category,
            name_ar='كعكة الاختبار',
            name_en='Test Cake',
            description_ar='وصف عربي خاص',
            description_en='A dedicated English description',
            price='12.00',
            is_featured=True,
            is_available=True,
        )
        response = self.client.get(f"{reverse('restaurant:home')}?lang=en")
        self.assertContains(response, 'Test Cake')
        self.assertContains(response, 'A dedicated English description')
        self.assertContains(response, 'Order dish')

    def test_absolute_open_graph_image_url_is_not_prefixed(self):
        site = RestaurantSettings.load()
        site.hero_image_url = 'https://cdn.example.com/hero.jpg'
        site.save()
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'content="https://cdn.example.com/hero.jpg"')
        self.assertNotContains(response, 'testserverhttps://cdn.example.com')

    def test_reservation_endpoint_is_rate_limited(self):
        for _ in range(5):
            response = self.client.post(reverse('restaurant:create_reservation'), {})
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('restaurant:create_reservation'), {})
        self.assertEqual(response.status_code, 429)

    def test_all_active_categories_are_rendered(self):
        for index in range(7):
            Category.objects.create(name_ar=f'قسم {index}', name_en=f'Category {index}')
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'data-filter="category-6"')

    def test_reservation_date_has_today_as_minimum(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, f'min="{date.today().isoformat()}"')
        self.assertContains(response, 'name="guests" value="2" min="1"')

    def test_social_post_without_url_is_not_a_dead_link(self):
        SocialPost.objects.create(title='Static image', image_url='https://cdn.example.com/post.jpg')
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'role="img" aria-label="Static image"')

    def test_invalid_reservation_phone_is_rejected(self):
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Invalid Phone',
                'phone': 'abc',
                'date': (date.today() + timedelta(days=1)).isoformat(),
                'time': '19:30',
                'guests': 2,
            }, follow=True,
        )
        self.assertContains(response, 'أدخل رقم جوال صحيحًا')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_header_order_button_follows_language(self):
        response = self.client.get(f"{reverse('restaurant:home')}?lang=en")
        self.assertContains(response, '<b>Order on WhatsApp</b>')
        response = self.client.get(f"{reverse('restaurant:home')}?lang=ar")
        self.assertContains(response, '<b>اطلب الآن عبر واتساب</b>')

    def test_about_section_and_menu_title_are_rendered(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'id="about"')
        self.assertContains(response, 'من نحن')
        self.assertContains(response, 'استكشف أقسام القائمة')

    def test_about_section_can_be_hidden(self):
        site = RestaurantSettings.load()
        site.show_about = False
        site.save()
        response = self.client.get(reverse('restaurant:home'))
        self.assertNotContains(response, 'id="about"')

    def test_seo_head_tags_are_present(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'hreflang="ar"')
        self.assertContains(response, 'hreflang="en"')
        self.assertContains(response, 'application/ld+json')
        self.assertContains(response, 'property="og:url"')
        self.assertContains(response, 'rel="icon"')

    def test_robots_txt_and_sitemap_xml(self):
        robots = self.client.get('/robots.txt')
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, 'Sitemap:')
        self.assertContains(robots, 'Disallow: /admin/')
        sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, '<urlset')
        self.assertContains(sitemap, '/menu/')

    def test_standalone_menu_uses_the_live_catalog_and_cart(self):
        category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        item = MenuItem.objects.create(
            category=category,
            name_ar='وجبة المنيو',
            name_en='Menu Meal',
            price='32.00',
        )
        offer = Offer.objects.create(
            title_ar='عرض المنيو',
            title_en='Menu Offer',
            price_text_ar='55 شيكل',
            price_text_en='55 ILS',
        )
        order = Order.objects.create(source='online')
        OrderLine.objects.create(
            order=order,
            menu_item=item,
            name_ar=item.name_ar,
            name_en=item.name_en,
            quantity=2,
            unit_price=item.price,
        )

        response = self.client.get(reverse('restaurant:menu'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="menu-catalog"')
        self.assertContains(response, 'وجبة المنيو')
        self.assertContains(response, f'data-id="{item.pk}"')
        self.assertContains(response, 'class="mini-whatsapp js-add-item')
        self.assertContains(response, 'id="menu-search"')
        self.assertContains(response, 'id="menu-grid" data-page-size="6"')
        self.assertContains(response, 'id="menu-load-more"')
        self.assertContains(response, 'id="remaining-menu-count"')
        self.assertContains(response, 'class="menu-show-all-btn active"')
        self.assertContains(response, 'data-clear-search="true"')
        self.assertContains(response, 'عرض الكل')
        self.assertContains(response, 'id="menu-offers"')
        self.assertContains(response, 'عرض المنيو')
        self.assertContains(response, f'data-id="offer-{offer.pk}"')
        self.assertContains(response, 'data-offer="true"')
        html = response.content.decode()
        self.assertLess(html.index('id="menu-catalog"'), html.index('id="menu-best"'))
        self.assertLess(html.index('id="menu-best"'), html.index('id="menu-offers"'))

    def test_menu_category_query_marks_the_requested_category_active(self):
        category = Category.objects.create(
            name_ar='حلويات',
            name_en='Desserts',
            slug='desserts',
        )
        response = self.client.get(
            reverse('restaurant:menu'),
            {'category': category.slug},
        )
        self.assertContains(
            response,
            'class="category-card active" type="button" data-filter="desserts"',
        )

    def test_menu_language_switch_stays_on_the_menu_page(self):
        response = self.client.get(f"{reverse('restaurant:menu')}?lang=en")
        self.assertContains(response, f'href="{reverse("restaurant:menu")}?lang=ar"')
        self.assertContains(response, 'Full Menu')

    def test_homepage_has_a_clear_link_to_the_qr_menu(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(response, reverse('restaurant:menu'))
        self.assertContains(response, 'عرض المنيو في صفحة مستقلة')

    def test_no_external_cdn_scripts(self):
        response = self.client.get(reverse('restaurant:home'))
        self.assertNotContains(response, 'unpkg.com')
        self.assertContains(response, 'restaurant/js/lucide-slim.js')

    def test_duplicate_reservation_is_not_created(self):
        payload = {
            'full_name': 'Duplicate Guest',
            'phone': '+970000000001',
            'date': (date.today() + timedelta(days=1)).isoformat(),
            'time': '18:30',
            'guests': 2,
        }
        first = self.client.post(reverse('restaurant:create_reservation'), payload)
        second = self.client.post(reverse('restaurant:create_reservation'), payload, follow=True)
        self.assertTrue(first['Location'].startswith('https://wa.me/'))
        self.assertContains(second, 'يوجد حجز مطابق مسجل بالفعل')
        self.assertEqual(Reservation.objects.count(), 1)

    def test_relative_static_image_paths_are_valid_in_admin_forms(self):
        site = RestaurantSettings.load()
        site.hero_image_url = '/static/restaurant/img/v3/hero-b12.webp'
        SiteForm = modelform_factory(RestaurantSettings, fields='__all__')
        site_data = {
            name: (getattr(site, name).name if hasattr(getattr(site, name), 'name') else getattr(site, name))
            for name in SiteForm.base_fields
        }
        self.assertTrue(SiteForm(data=site_data, instance=site).is_valid())

        category = Category.objects.create(
            name_ar='صورة محلية',
            name_en='Local image',
            image_url='/static/restaurant/img/v3/pizza-960.webp',
        )
        CategoryForm = modelform_factory(Category, fields='__all__')
        category_data = {
            name: (getattr(category, name).name if hasattr(getattr(category, name), 'name') else getattr(category, name))
            for name in CategoryForm.base_fields
        }
        self.assertTrue(CategoryForm(data=category_data, instance=category).is_valid())

    def test_english_hero_stats_use_english_as_primary_text(self):
        HeroStat.objects.create(title_ar='جودة', title_en='Quality', is_active=True)
        response = self.client.get(f"{reverse('restaurant:home')}?lang=en")
        self.assertContains(response, '<b>Quality</b>')
        self.assertContains(response, '<small>جودة</small>')

    def test_hiding_menu_also_hides_dead_category_filters_and_nav_link(self):
        site = RestaurantSettings.load()
        site.show_featured = False
        site.save()
        response = self.client.get(reverse('restaurant:home'))
        self.assertNotContains(response, 'class="category-card')
        self.assertNotContains(response, 'class="menu-card')
        self.assertNotContains(response, 'href="#menu"')

    def test_main_navigation_follows_the_home_page_section_order(self):
        response = self.client.get(reverse('restaurant:home'))
        html = response.content.decode()
        nav = html[html.index('id="main-nav"'):html.index('</nav>')]
        anchors = ['#hero', '#menu', '#featured', '#offers', '#contact', '#about']
        positions = [nav.index(f'href="{anchor}"') for anchor in anchors]
        self.assertEqual(positions, sorted(positions))

    def test_social_title_and_branded_buttons_link_to_social_profiles(self):
        site = RestaurantSettings.load()
        site.instagram_url = 'https://www.instagram.com/b12restaurant/'
        site.facebook_url = 'https://www.facebook.com/b12restaurant/'
        site.save()
        response = self.client.get(reverse('restaurant:home'))
        self.assertContains(
            response,
            'class="social-title" href="https://www.instagram.com/b12restaurant/"',
        )
        self.assertContains(
            response,
            'class="social-facebook" href="https://www.facebook.com/b12restaurant/"',
        )
        self.assertContains(
            response,
            'class="social-instagram" href="https://www.instagram.com/b12restaurant/"',
        )
        self.assertContains(response, 'class="social-whatsapp js-open-cart"')

    def test_best_sellers_use_saved_online_and_cashier_order_quantities(self):
        category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        item = MenuItem.objects.create(
            category=category,
            name_ar='كباب الاختبار',
            name_en='Test Kebab',
            price='45.00',
        )
        online = Order.objects.create(source='online')
        cashier = Order.objects.create(
            source='cashier',
            fulfillment='dine_in',
            customer_count=4,
        )
        OrderLine.objects.create(
            order=online,
            menu_item=item,
            name_ar=item.name_ar,
            name_en=item.name_en,
            quantity=2,
            unit_price=item.price,
        )
        OrderLine.objects.create(
            order=cashier,
            menu_item=item,
            name_ar=item.name_ar,
            name_en=item.name_en,
            quantity=3,
            unit_price=item.price,
        )

        response = self.client.get(reverse('restaurant:home'))

        self.assertContains(response, 'id="best-sellers"')
        self.assertContains(response, 'href="#best-sellers"')
        self.assertContains(response, 'كباب الاختبار')
        self.assertContains(response, '2 أونلاين')
        self.assertContains(response, '3 داخل المطعم')

    def test_phone_with_letters_is_rejected_even_when_it_has_enough_digits(self):
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Invalid Phone',
                'phone': 'abc1234567',
                'date': (date.today() + timedelta(days=1)).isoformat(),
                'time': '19:30',
                'guests': 2,
            },
            follow=True,
        )
        self.assertContains(response, 'أدخل رقم جوال صحيحًا')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_reservation_beyond_configured_advance_window_is_rejected(self):
        site = RestaurantSettings.load()
        site.max_reservation_days_ahead = 7
        site.save()
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'Far Future',
                'phone': '+970591234567',
                'date': (date.today() + timedelta(days=8)).isoformat(),
                'time': '19:30',
                'guests': 2,
            },
            follow=True,
        )
        self.assertContains(response, 'يمكن الحجز خلال 7 يومًا فقط')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_full_reservation_slot_is_rejected(self):
        site = RestaurantSettings.load()
        site.max_reservations_per_slot = 2
        site.save()
        reservation_date = date.today() + timedelta(days=1)
        for index in range(2):
            Reservation.objects.create(
                full_name=f'Guest {index}',
                phone=f'97059123456{index}',
                date=reservation_date,
                time='19:30',
                guests=2,
            )
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {
                'full_name': 'No Capacity',
                'phone': '+970591239999',
                'date': reservation_date.isoformat(),
                'time': '19:30',
                'guests': 2,
            },
            follow=True,
        )
        self.assertContains(response, 'هذه الفترة ممتلئة')
        self.assertEqual(Reservation.objects.count(), 2)

    @override_settings(TRUSTED_PROXY_HOPS=0)
    def test_spoofed_forwarded_for_does_not_bypass_rate_limit(self):
        cache.clear()
        for index in range(5):
            response = self.client.post(
                reverse('restaurant:create_reservation'),
                {},
                HTTP_X_FORWARDED_FOR=f'203.0.113.{index}',
            )
            self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse('restaurant:create_reservation'),
            {},
            HTTP_X_FORWARDED_FOR='198.51.100.99',
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response['Retry-After'], '600')


class DashboardAccessTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.url = reverse('restaurant:dashboard')

    def test_anonymous_visitor_is_sent_to_the_admin_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_signed_in_customer_without_staff_access_is_refused(self):
        User.objects.create_user('customer', password='pw-not-staff-1234')
        self.client.login(username='customer', password='pw-not-staff-1234')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_staff_member_sees_the_dashboard(self):
        User.objects.create_user('manager', password='pw-manager-1234', is_staff=True)
        self.client.login(username='manager', password='pw-manager-1234')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'قائمة العملاء')
        self.assertContains(response, 'ضيوف الليلة')

    def test_staff_without_change_permission_cannot_confirm_from_the_list(self):
        User.objects.create_user('viewer', password='pw-viewer-1234', is_staff=True)
        self.client.login(username='viewer', password='pw-viewer-1234')
        Reservation.objects.create(
            full_name='زائر', phone='0597000000',
            date=timezone.localdate(), time=time(20, 0), guests=2,
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'زائر')
        self.assertNotContains(response, 'value="confirmed"')

    def test_robots_txt_keeps_the_dashboard_out_of_search(self):
        response = self.client.get(reverse('restaurant:robots'))
        self.assertContains(response, 'Disallow: /dashboard/')


class DashboardStatusActionTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.manager = User.objects.create_user('boss', password='pw-boss-1234', is_staff=True)
        self.manager.user_permissions.add(
            Permission.objects.get(codename='change_reservation')
        )
        self.client.login(username='boss', password='pw-boss-1234')
        self.reservation = Reservation.objects.create(
            full_name='سامي', phone='0597111222',
            date=timezone.localdate(), time=time(20, 0), guests=4,
        )
        self.url = reverse(
            'restaurant:dashboard_reservation_status', args=[self.reservation.pk]
        )

    def test_manager_confirms_a_booking(self):
        response = self.client.post(self.url, {'status': 'confirmed'})
        self.assertEqual(response.status_code, 302)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'confirmed')

    def test_it_returns_to_the_same_filtered_list(self):
        response = self.client.post(
            self.url, {'status': 'contacted', 'q': 'سامي', 'segment': 'vip', 'page': '2'}
        )
        self.assertIn('segment=vip', response['Location'])
        self.assertIn('page=2', response['Location'])

    def test_an_unknown_status_is_rejected(self):
        response = self.client.post(self.url, {'status': 'seated'}, follow=True)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'new')
        self.assertContains(response, 'حالة الحجز غير معروفة')

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_staff_without_permission_cannot_change_a_booking(self):
        User.objects.create_user('waiter', password='pw-waiter-1234', is_staff=True)
        self.client.login(username='waiter', password='pw-waiter-1234')
        response = self.client.post(self.url, {'status': 'cancelled'})
        self.assertEqual(response.status_code, 403)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'new')


class CustomerRecordTests(TestCase):
    """Customers are grouped by phone number and never stored separately."""

    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.today = date(2030, 6, 20)

    def _book(self, day, phone='0597111222', name='سامي', guests=2, status='confirmed', occasion=''):
        return Reservation.objects.create(
            full_name=name, phone=phone, date=day, time=time(20, 0),
            guests=guests, status=status, occasion=occasion,
        )

    def test_the_same_phone_written_differently_is_one_customer(self):
        self._book(self.today - timedelta(days=10), phone='0597111222')
        self._book(self.today - timedelta(days=3), phone='059-711-1222')
        customers = crm.build_customers(self.today)
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0]['visits'], 2)

    def test_the_most_recent_name_wins(self):
        self._book(self.today - timedelta(days=20), name='سامي')
        self._book(self.today - timedelta(days=2), name='سامي حجازي')
        self.assertEqual(crm.build_customers(self.today)[0]['name'], 'سامي حجازي')

    def test_a_cancelled_booking_is_not_a_visit(self):
        self._book(self.today - timedelta(days=5), status='cancelled')
        customer = crm.build_customers(self.today)[0]
        self.assertEqual(customer['visits'], 0)
        self.assertEqual(customer['cancellations'], 1)

    def test_a_future_booking_counts_as_upcoming_not_as_a_visit(self):
        self._book(self.today + timedelta(days=4))
        customer = crm.build_customers(self.today)[0]
        self.assertEqual(customer['visits'], 0)
        self.assertEqual(customer['upcoming'], 1)
        self.assertEqual(customer['next_visit'], self.today + timedelta(days=4))

    def test_covers_add_up_across_visits(self):
        self._book(self.today - timedelta(days=9), guests=4)
        self._book(self.today - timedelta(days=2), guests=6)
        self.assertEqual(crm.build_customers(self.today)[0]['covers'], 10)

    def test_one_visit_is_a_new_customer(self):
        self._book(self.today - timedelta(days=1))
        self.assertEqual(crm.build_customers(self.today)[0]['segment'], 'new')

    def test_three_recent_visits_is_a_regular(self):
        for offset in (2, 9, 16):
            self._book(self.today - timedelta(days=offset))
        self.assertEqual(crm.build_customers(self.today)[0]['segment'], 'regular')

    def test_five_recent_visits_is_a_vip(self):
        for offset in (1, 8, 15, 22, 29):
            self._book(self.today - timedelta(days=offset))
        self.assertEqual(crm.build_customers(self.today)[0]['segment'], 'vip')

    def test_a_vip_who_stopped_coming_is_flagged_for_follow_up(self):
        for offset in (100, 110, 120, 130, 140):
            self._book(self.today - timedelta(days=offset))
        customer = crm.build_customers(self.today)[0]
        self.assertEqual(customer['segment'], 'lapsed')
        self.assertEqual(customer['visits'], 5)

    def test_a_first_time_visitor_from_long_ago_is_not_called_lapsed(self):
        """Lapsed means a habit was broken, so it needs at least two visits."""
        self._book(self.today - timedelta(days=200))
        self.assertEqual(crm.build_customers(self.today)[0]['segment'], 'new')

    def test_the_rhythm_covers_twelve_months_ending_this_month(self):
        self._book(self.today - timedelta(days=2))
        rhythm = crm.build_customers(self.today)[0]['rhythm']
        self.assertEqual(len(rhythm), 12)
        self.assertEqual(rhythm[-1]['visits'], 1)
        self.assertEqual(rhythm[0]['visits'], 0)

    def test_bookings_without_a_usable_phone_are_skipped(self):
        self._book(self.today - timedelta(days=1), phone='---')
        self.assertEqual(crm.build_customers(self.today), [])


class CustomerFilterTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.today = date(2030, 6, 20)
        Reservation.objects.create(
            full_name='ليلى شحادة', phone='0597111222', date=self.today - timedelta(days=2),
            time=time(20, 0), guests=2, status='confirmed',
        )
        Reservation.objects.create(
            full_name='كريم زقوت', phone='0598333444', date=self.today - timedelta(days=5),
            time=time(21, 0), guests=4, status='confirmed',
        )
        self.customers = crm.build_customers(self.today)

    def test_search_matches_part_of_a_name(self):
        found = crm.filter_customers(self.customers, query='ليلى')
        self.assertEqual([item['name'] for item in found], ['ليلى شحادة'])

    def test_search_matches_part_of_a_phone_number(self):
        found = crm.filter_customers(self.customers, query='333444')
        self.assertEqual([item['name'] for item in found], ['كريم زقوت'])

    def test_search_ignores_dashes_in_the_typed_number(self):
        found = crm.filter_customers(self.customers, query='059-833-3444')
        self.assertEqual(len(found), 1)

    def test_an_unknown_segment_is_ignored_rather_than_emptying_the_list(self):
        found = crm.filter_customers(self.customers, segment='platinum')
        self.assertEqual(len(found), 2)

    def test_sorting_by_visits_puts_the_most_frequent_first(self):
        Reservation.objects.create(
            full_name='كريم زقوت', phone='0598333444', date=self.today - timedelta(days=1),
            time=time(21, 0), guests=4, status='confirmed',
        )
        customers = crm.sort_customers(crm.build_customers(self.today), 'visits')
        self.assertEqual(customers[0]['name'], 'كريم زقوت')

    def test_sorting_by_last_visit_puts_the_most_recent_first(self):
        customers = crm.sort_customers(self.customers, 'last')
        self.assertEqual(customers[0]['name'], 'ليلى شحادة')


class TonightTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.today = timezone.localdate()

    def _book(self, day, status='confirmed'):
        return Reservation.objects.create(
            full_name='سامي', phone='0597111222', date=day,
            time=time(20, 0), guests=2, status=status,
        )

    def test_a_guest_with_no_history_is_a_first_visit(self):
        self._book(self.today)
        row = crm.tonight(crm.build_customers(self.today), self.today)[0]
        self.assertTrue(row['is_first_visit'])
        self.assertEqual(row['visit_badge'], 'أول زيارة')

    def test_tonight_is_not_counted_as_a_previous_visit(self):
        """Two earlier visits plus tonight must read as visit number three."""
        self._book(self.today - timedelta(days=30))
        self._book(self.today - timedelta(days=10))
        self._book(self.today)
        row = crm.tonight(crm.build_customers(self.today), self.today)[0]
        self.assertEqual(row['visit_badge'], 'الزيارة رقم 3')
        self.assertTrue(row['is_regular'])

    def test_cancelled_bookings_are_not_shown_tonight(self):
        self._book(self.today, status='cancelled')
        self.assertEqual(crm.tonight(crm.build_customers(self.today), self.today), [])


class CustomerDashboardViewTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        User.objects.create_user('manager', password='pw-manager-1234', is_staff=True)
        self.client.login(username='manager', password='pw-manager-1234')
        self.url = reverse('restaurant:dashboard')
        today = timezone.localdate()
        for offset in (2, 30, 60):
            Reservation.objects.create(
                full_name='ليلى شحادة', phone='0597111222', date=today - timedelta(days=offset),
                time=time(20, 0), guests=3, status='confirmed',
            )

    def test_the_customer_appears_with_a_visit_count(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'ليلى شحادة')
        self.assertContains(response, 'متكرر')

    def test_search_narrows_the_list(self):
        response = self.client.get(self.url, {'q': 'لا-أحد-بهذا-الاسم'})
        self.assertNotContains(response, 'ليلى شحادة')
        self.assertContains(response, 'لا عميل يطابق هذا البحث')

    def test_an_unknown_sort_falls_back_instead_of_erroring(self):
        response = self.client.get(self.url, {'sort': 'drop table'})
        self.assertEqual(response.status_code, 200)

    def test_an_empty_restaurant_explains_itself(self):
        Reservation.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, 'ستظهر أسماء العملاء هنا')


class AdminSkinTests(TestCase):
    """The admin templates are overridden, so they need a smoke test."""

    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        User.objects.create_superuser('owner', 'owner@example.com', 'pw-owner-1234')
        self.client.login(username='owner', password='pw-owner-1234')

    def test_the_start_page_shows_the_stat_tiles(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="b12-stats"')
        self.assertContains(response, 'حجوزات الليلة')
        self.assertContains(response, 'تنتظر ردًا')

    def test_the_start_page_counts_bookings_waiting_for_a_reply(self):
        for _ in range(3):
            Reservation.objects.create(
                full_name='ضيف', phone='0597000111', date=timezone.localdate(),
                time=time(20, 0), guests=2, status='new',
            )
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'راجعها الآن')

    def test_every_admin_page_links_to_the_customer_dashboard(self):
        response = self.client.get(reverse('admin:restaurant_reservation_changelist'))
        self.assertContains(response, reverse('restaurant:dashboard'))
        self.assertContains(response, 'b12-desk-link')

    def test_the_admin_loads_the_b12_stylesheet(self):
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'restaurant/css/admin.css')

    def test_a_staff_user_without_model_permissions_still_gets_a_page(self):
        User.objects.create_user('greeter', password='pw-greeter-1234', is_staff=True)
        self.client.login(username='greeter', password='pw-greeter-1234')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)


class RelativeDatePhraseTests(TestCase):
    def test_the_dual_takes_the_genitive_after_a_preposition(self):
        """قبل يومين, not قبل يومان — the preposition governs the case."""
        self.assertEqual(crm._relative_day_phrase(2), 'قبل يومين')
        self.assertEqual(crm._relative_day_phrase(60), 'قبل شهرين')

    def test_recent_days_read_naturally(self):
        self.assertEqual(crm._relative_day_phrase(0), 'اليوم')
        self.assertEqual(crm._relative_day_phrase(1), 'أمس')
        self.assertEqual(crm._relative_day_phrase(5), 'قبل 5 أيام')
        self.assertEqual(crm._relative_day_phrase(17), 'قبل 17 يومًا')


class ControlPanelTests(TestCase):
    """The panel replaces the Django admin for content, so it needs teeth."""

    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        User.objects.create_superuser('boss2', 'b@example.com', 'pw-boss2-1234')
        self.client.login(username='boss2', password='pw-boss2-1234')
        self.category = Category.objects.create(name_ar='مشاوي', name_en='Grills')

    def test_unknown_section_is_a_404(self):
        response = self.client.get(reverse('restaurant:panel_list', args=['nonsense']))
        self.assertEqual(response.status_code, 404)

    def test_a_section_lists_its_records(self):
        response = self.client.get(reverse('restaurant:panel_list', args=['categories']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مشاوي')

    def test_search_narrows_a_section(self):
        Category.objects.create(name_ar='حلويات', name_en='Sweets')
        response = self.client.get(
            reverse('restaurant:panel_list', args=['categories']), {'q': 'حلويات'}
        )
        self.assertContains(response, 'حلويات')
        self.assertNotContains(response, 'مشاوي')

    def test_adding_a_record_saves_it(self):
        response = self.client.post(reverse('restaurant:panel_add', args=['offers']), {
            'title_ar': 'عرض العائلة', 'title_en': 'Family Deal',
            'description_ar': '', 'description_en': '',
            'price_text_ar': '99', 'price_text_en': '99',
            'image_url': '', 'display_order': 1, 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Offer.objects.filter(title_ar='عرض العائلة').exists())

    def test_editing_a_record_updates_it(self):
        response = self.client.post(
            reverse('restaurant:panel_edit', args=['categories', self.category.pk]),
            {'name_ar': 'مشاوي شرقية', 'name_en': 'Grills', 'slug': 'grills',
             'icon': 'skewer', 'image_url': '', 'display_order': 0, 'is_active': 'on'},
        )
        self.assertEqual(response.status_code, 302)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name_ar, 'مشاوي شرقية')

    def test_an_invalid_form_redisplays_instead_of_saving(self):
        response = self.client.post(
            reverse('restaurant:panel_edit', args=['categories', self.category.pk]),
            {'name_ar': '', 'name_en': '', 'slug': '', 'icon': 'skewer',
             'image_url': '', 'display_order': 0},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'راجع الحقول')
        self.category.refresh_from_db()
        self.assertEqual(self.category.name_ar, 'مشاوي')

    def test_toggling_a_boolean_flips_it(self):
        self.assertTrue(self.category.is_active)
        response = self.client.post(
            reverse('restaurant:panel_toggle', args=['categories', self.category.pk]),
            {'field': 'is_active'},
        )
        self.assertEqual(response.status_code, 302)
        self.category.refresh_from_db()
        self.assertFalse(self.category.is_active)

    def test_toggling_a_field_outside_the_allowlist_is_refused(self):
        """Otherwise any editable column could be flipped by a crafted post."""
        response = self.client.post(
            reverse('restaurant:panel_toggle', args=['categories', self.category.pk]),
            {'field': 'name_ar'},
        )
        self.assertEqual(response.status_code, 403)

    def test_deleting_a_record_removes_it(self):
        offer = Offer.objects.create(title_ar='مؤقت', title_en='Temp')
        response = self.client.post(reverse('restaurant:panel_delete', args=['offers', offer.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Offer.objects.filter(pk=offer.pk).exists())

    def test_deleting_a_category_that_still_has_dishes_is_explained(self):
        MenuItem.objects.create(
            category=self.category, name_ar='كباب', name_en='Kebab', price='30.00',
        )
        response = self.client.post(
            reverse('restaurant:panel_delete', args=['categories', self.category.pk]),
            follow=True,
        )
        self.assertContains(response, 'تعذر حذف')
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_delete_needs_a_post(self):
        response = self.client.get(
            reverse('restaurant:panel_delete', args=['categories', self.category.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_the_settings_page_saves_a_change(self):
        from django.db.models.fields.files import FieldFile

        from .admin import RestaurantSettingsAdminForm

        blank = RestaurantSettingsAdminForm(instance=RestaurantSettings.load())
        data = {}
        for name in blank.fields:
            value = blank.initial.get(name)
            if value is None or isinstance(value, FieldFile):
                continue  # uploaded files are posted separately
            if isinstance(value, bool):
                if value:
                    data[name] = 'on'
            else:
                data[name] = str(value)
        data['name_ar'] = 'مطعم B12 الجديد'

        response = self.client.post(reverse('restaurant:panel_settings'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RestaurantSettings.load().name_ar, 'مطعم B12 الجديد')


class ControlPanelPermissionTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        self.category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        self.waiter = User.objects.create_user(
            'waiter2', password='pw-waiter2-1234', is_staff=True
        )
        self.client.login(username='waiter2', password='pw-waiter2-1234')

    def test_staff_without_view_permission_is_refused(self):
        response = self.client.get(reverse('restaurant:panel_list', args=['categories']))
        self.assertEqual(response.status_code, 403)

    def test_view_permission_alone_hides_the_delete_button(self):
        self.waiter.user_permissions.add(Permission.objects.get(codename='view_category'))
        response = self.client.get(reverse('restaurant:panel_list', args=['categories']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مشاوي')
        self.assertNotContains(response, 'btn-danger')

    def test_view_permission_alone_cannot_delete(self):
        self.waiter.user_permissions.add(Permission.objects.get(codename='view_category'))
        response = self.client.post(
            reverse('restaurant:panel_delete', args=['categories', self.category.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_the_sidebar_only_lists_permitted_sections(self):
        self.waiter.user_permissions.add(Permission.objects.get(codename='view_offer'))
        response = self.client.get(reverse('restaurant:dashboard'))
        self.assertContains(response, 'العروض')
        self.assertNotContains(response, 'أقسام القائمة')

    def test_settings_needs_its_own_permission(self):
        response = self.client.get(reverse('restaurant:panel_settings'))
        self.assertEqual(response.status_code, 403)


class CashierOrderTests(TestCase):
    def setUp(self):
        cache.clear()
        self.site = RestaurantSettings.load()
        self.category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        self.item = MenuItem.objects.create(
            category=self.category,
            name_ar='كباب',
            name_en='Kebab',
            price='45.00',
        )
        self.cashier = User.objects.create_user(
            'cashier',
            password='cashier-password-1234',
            is_staff=True,
        )
        self.client.login(username='cashier', password='cashier-password-1234')

    def test_cashier_page_requires_add_order_permission(self):
        response = self.client.get(reverse('restaurant:cashier'))
        self.assertEqual(response.status_code, 403)

    def test_cashier_page_is_available_to_authorized_staff(self):
        self.cashier.user_permissions.add(Permission.objects.get(codename='add_order'))
        response = self.client.get(reverse('restaurant:cashier'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="quantity_')

    def test_cashier_order_is_saved_and_priced_from_the_database(self):
        self.cashier.user_permissions.add(Permission.objects.get(codename='add_order'))
        response = self.client.post(reverse('restaurant:cashier'), {
            'customer_name': 'زبون الطاولة',
            'customer_count': '4',
            'table_number': '12',
            'notes': 'بدون بصل',
            f'quantity_{self.item.pk}': '3',
            'price': '1',
        })

        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(source='cashier')
        self.assertEqual(order.fulfillment, 'dine_in')
        self.assertEqual(order.status, 'confirmed')
        self.assertEqual(order.customer_count, 4)
        self.assertEqual(order.table_number, '12')
        self.assertEqual(order.cashier, self.cashier)
        self.assertEqual(order.total, Decimal('135.00'))
        self.assertEqual(order.lines.get().quantity, 3)

    def test_cashier_dashboard_counts_inside_and_online_customers(self):
        self.cashier.user_permissions.add(Permission.objects.get(codename='add_order'))
        Order.objects.create(source='online', customer_count=1)
        Order.objects.create(
            source='cashier',
            fulfillment='dine_in',
            customer_count=5,
        )

        response = self.client.get(reverse('restaurant:cashier'))

        self.assertEqual(response.context['stats']['inside_customers'], 5)
        self.assertEqual(response.context['stats']['outside_customers'], 1)


class OrderPricingTests(TestCase):
    """The whole point: the browser cannot influence what is owed."""

    def setUp(self):
        cache.clear()
        site = RestaurantSettings.load()
        site.whatsapp_number = '972597862389'
        site.save()
        self.category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        self.kebab = MenuItem.objects.create(
            category=self.category, name_ar='كباب', name_en='Kebab', price='45.00',
        )
        self.juice = MenuItem.objects.create(
            category=self.category, name_ar='عصير', name_en='Juice', price='12.00',
        )
        self.url = reverse('restaurant:create_order')

    def _post(self, payload):
        return self.client.post(self.url, data=payload, content_type='application/json')

    def test_the_server_prices_the_order_from_the_menu(self):
        response = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 2}]})
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(code=response.json()['code'])
        self.assertEqual(order.total, Decimal('90.00'))

    def test_a_price_sent_by_the_browser_is_ignored(self):
        """The original hole: editing localStorage changed what was sent."""
        response = self._post({'items': [
            {'id': str(self.kebab.pk), 'qty': 1, 'price': 1, 'nameAr': 'ستيك مجاني'},
        ]})
        order = Order.objects.get(code=response.json()['code'])
        self.assertEqual(order.total, Decimal('45.00'))
        self.assertEqual(order.lines.first().name_ar, 'كباب')

    def test_totals_add_up_across_several_dishes(self):
        response = self._post({'items': [
            {'id': str(self.kebab.pk), 'qty': 2},
            {'id': str(self.juice.pk), 'qty': 3},
        ]})
        order = Order.objects.get(code=response.json()['code'])
        self.assertEqual(order.total, Decimal('126.00'))

    def test_an_unavailable_dish_is_dropped(self):
        self.juice.is_available = False
        self.juice.save()
        response = self._post({'items': [
            {'id': str(self.kebab.pk), 'qty': 1},
            {'id': str(self.juice.pk), 'qty': 5},
        ]})
        order = Order.objects.get(code=response.json()['code'])
        self.assertEqual(order.lines.count(), 1)
        self.assertEqual(order.total, Decimal('45.00'))

    def test_an_order_of_only_unavailable_dishes_is_refused(self):
        self.kebab.is_available = False
        self.kebab.save()
        response = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 1}]})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Order.objects.count(), 0)

    def test_an_unknown_dish_id_creates_nothing(self):
        response = self._post({'items': [{'id': '99999', 'qty': 1}]})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Order.objects.count(), 0)

    def test_quantities_outside_the_allowed_range_are_dropped(self):
        response = self._post({'items': [
            {'id': str(self.kebab.pk), 'qty': 0},
            {'id': str(self.juice.pk), 'qty': 9999},
        ]})
        self.assertEqual(response.status_code, 400)

    def test_repeated_ids_are_merged_rather_than_duplicated(self):
        response = self._post({'items': [
            {'id': str(self.kebab.pk), 'qty': 1},
            {'id': str(self.kebab.pk), 'qty': 2},
        ]})
        order = Order.objects.get(code=response.json()['code'])
        self.assertEqual(order.lines.count(), 1)
        self.assertEqual(order.lines.first().quantity, 3)
        self.assertEqual(order.total, Decimal('135.00'))

    def test_an_offer_is_quoted_not_computed(self):
        offer = Offer.objects.create(
            title_ar='عرض العائلة', title_en='Family', price_text_ar='99 شيكل',
        )
        response = self._post({'items': [{'id': f'offer-{offer.pk}', 'qty': 1}]})
        order = Order.objects.get(code=response.json()['code'])
        self.assertTrue(order.has_unpriced_lines)
        self.assertEqual(order.total, Decimal('0'))
        self.assertFalse(order.lines.first().is_priced)

    def test_line_prices_are_a_snapshot_not_a_live_lookup(self):
        """Raising the menu price later must not rewrite a past order."""
        response = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 1}]})
        order = Order.objects.get(code=response.json()['code'])
        self.kebab.price = Decimal('80.00')
        self.kebab.save()
        order.refresh_from_db()
        self.assertEqual(order.total, Decimal('45.00'))
        self.assertEqual(order.lines.first().unit_price, Decimal('45.00'))

    def test_deleting_a_dish_keeps_the_order_readable(self):
        response = self._post({'items': [{'id': str(self.juice.pk), 'qty': 1}]})
        order = Order.objects.get(code=response.json()['code'])
        self.juice.delete()
        line = order.lines.first()
        line.refresh_from_db()
        self.assertIsNone(line.menu_item)
        self.assertEqual(line.name_ar, 'عصير')

    def test_delivery_requires_name_phone_and_address(self):
        response = self._post({
            'items': [{'id': str(self.kebab.pk), 'qty': 1}],
            'fulfillment': 'delivery', 'name': '', 'phone': '', 'address': '',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_pickup_does_not_require_contact_details(self):
        response = self._post({
            'items': [{'id': str(self.kebab.pk), 'qty': 1}], 'fulfillment': 'pickup',
        })
        self.assertEqual(response.status_code, 200)

    def test_the_whatsapp_message_carries_the_code_and_no_prices(self):
        response = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 2}]})
        data = response.json()
        self.assertIn(data['code'], data['message'])
        self.assertNotIn('90', data['message'])
        self.assertTrue(data['whatsapp_url'].startswith('https://wa.me/972597862389'))

    def test_the_link_sits_alone_so_whatsapp_makes_it_tappable(self):
        """A URL sharing a line with Arabic loses its boundaries to bidi."""
        data = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 1}]}).json()
        last_line = data['message'].split('\n')[-1]
        self.assertEqual(last_line, data['order_url'])
        self.assertFalse(any('؀' <= ch <= 'ۿ' for ch in last_line))

    def test_nothing_precedes_the_link_on_its_line(self):
        """A leading character stops WhatsApp linkifying it and gets copied
        into the address bar along with the URL."""
        data = self._post({'items': [{'id': str(self.kebab.pk), 'qty': 1}]}).json()
        last_line = data['message'].split('\n')[-1]
        self.assertTrue(last_line.startswith('http'))
        self.assertEqual(last_line, last_line.strip())

    def test_a_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_malformed_json_is_refused(self):
        response = self.client.post(self.url, data='not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_an_empty_cart_is_refused(self):
        self.assertEqual(self._post({'items': []}).status_code, 400)

    def test_the_endpoint_is_rate_limited(self):
        payload = {'items': [{'id': str(self.kebab.pk), 'qty': 1}]}
        for _ in range(12):
            self.assertEqual(self._post(payload).status_code, 200)
        self.assertEqual(self._post(payload).status_code, 429)

    def _refusals(self):
        """One call per way the endpoint can refuse an order."""
        self.client.post(self.url, data='not json', content_type='application/json')
        yield self.client.post(self.url, data='not json', content_type='application/json')
        yield self._post({'items': []})
        yield self._post({'items': [{'id': str(self.kebab.pk), 'qty': 1}] * 41})
        yield self._post({'items': [{'id': 'not-a-dish', 'qty': 1}]})
        yield self._post({
            'items': [{'id': str(self.kebab.pk), 'qty': 1}],
            'fulfillment': 'delivery',
        })

    def test_a_refusal_is_written_in_the_language_the_visitor_chose(self):
        # An Arabic-only refusal is unreadable to a visitor who switched the
        # site to English, and these messages are shown verbatim: they are
        # JSON, so no template gets the chance to translate them.
        self.client.get(reverse('restaurant:home'), {'lang': 'en'})
        for response in self._refusals():
            with self.subTest(status=response.status_code):
                message = response.json()['error']
                self.assertNotEqual(message, '')
                self.assertFalse(
                    any('؀' <= character <= 'ۿ' for character in message),
                    f'English visitor was shown Arabic: {message}',
                )

        cache.clear()
        self.client.get(reverse('restaurant:home'), {'lang': 'ar'})
        for response in self._refusals():
            with self.subTest(status=response.status_code):
                message = response.json()['error']
                self.assertTrue(
                    any('؀' <= character <= 'ۿ' for character in message),
                    f'Arabic visitor was shown English: {message}',
                )


class OrderCodeTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()

    def test_codes_are_unique_across_many_orders(self):
        codes = {Order.objects.create().code for _ in range(60)}
        self.assertEqual(len(codes), 60)

    def test_the_code_avoids_characters_that_are_misread_aloud(self):
        for _ in range(30):
            body = Order.objects.create().code.removeprefix('B12-')
            self.assertFalse(set(body) & set('IO01'))


class OrderPagesTests(TestCase):
    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        item = MenuItem.objects.create(
            category=category, name_ar='كباب', name_en='Kebab', price='45.00',
        )
        response = self.client.post(
            reverse('restaurant:create_order'),
            data={'items': [{'id': str(item.pk), 'qty': 2}], 'notes': 'بدون بصل'},
            content_type='application/json',
        )
        self.order = Order.objects.get(code=response.json()['code'])

    def test_the_order_page_shows_the_server_total(self):
        response = self.client.get(reverse('restaurant:order_detail', args=[self.order.token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.code)
        self.assertContains(response, '90')
        self.assertContains(response, 'بدون بصل')

    def test_an_unknown_code_is_a_404(self):
        response = self.client.get(reverse('restaurant:order_detail', args=['not-a-real-token']))
        self.assertEqual(response.status_code, 404)

    def test_the_receipt_renders_as_a_png(self):
        response = self.client.get(reverse('restaurant:order_receipt', args=[self.order.token]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))
        self.assertGreater(len(response.content), 2000)

    def test_the_receipt_is_kept_out_of_search_engines(self):
        response = self.client.get(reverse('restaurant:order_receipt', args=[self.order.token]))
        self.assertIn('noindex', response['X-Robots-Tag'])

    def test_orders_appear_in_the_control_panel(self):
        User.objects.create_superuser('boss3', 'b3@example.com', 'pw-boss3-1234')
        self.client.login(username='boss3', password='pw-boss3-1234')
        response = self.client.get(reverse('restaurant:panel_list', args=['orders']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.code)

    def test_staff_cannot_rewrite_the_total_from_the_panel(self):
        """Status moves; money does not."""
        User.objects.create_superuser('boss4', 'b4@example.com', 'pw-boss4-1234')
        self.client.login(username='boss4', password='pw-boss4-1234')
        self.client.post(
            reverse('restaurant:panel_edit', args=['orders', self.order.pk]),
            {'status': 'confirmed', 'fulfillment': 'pickup', 'customer_name': '',
             'phone': '', 'address': '', 'notes': '', 'total': '1.00'},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')
        self.assertEqual(self.order.total, Decimal('90.00'))


class ArabicReceiptRenderingTests(TestCase):
    """Guards the font swap: Cairo lacked the isolated letterforms."""

    def test_every_glyph_the_receipt_needs_exists_in_the_bundled_font(self):
        import arabic_reshaper
        from fontTools.ttLib import TTFont

        from .receipt import REGULAR, SEMIBOLD

        sample = (
            'رقم الطلب الإجمالي كباب مشوي مشكل عصير ليمون بالنعناع بيتزا '
            'استلام من المطعم ديليفري الاسم الجوال العنوان ملاحظات '
            'صدرت هذه الفاتورة من موقع المطعم والأسعار محسوبة على الخادم '
            'للتأكد ابحث عن الرقم في لوحة المطعم يحدد عند التأكيد بدون بصل'
        )
        needed = {ord(character) for character in arabic_reshaper.reshape(sample)}
        needed |= {ord(character) for character in 'B12-ACDEFGHJKLMNPQRSTUVWXYZ0123456789 ₪×·/:'}

        for path in (REGULAR, SEMIBOLD):
            covered = set(TTFont(str(path)).getBestCmap().keys())
            missing = sorted(hex(code) for code in needed - covered)
            self.assertEqual(missing, [], f'{path.name} is missing {missing}')


class OrderUrlPrivacyTests(TestCase):
    """The order page carries a customer's name, phone and address."""

    def setUp(self):
        cache.clear()
        RestaurantSettings.load()
        category = Category.objects.create(name_ar='مشاوي', name_en='Grills')
        self.item = MenuItem.objects.create(
            category=category, name_ar='كباب', name_en='Kebab', price='45.00',
        )
        response = self.client.post(
            reverse('restaurant:create_order'),
            data={
                'items': [{'id': str(self.item.pk), 'qty': 1}],
                'fulfillment': 'delivery', 'name': 'أحمد', 'phone': '0597862389',
                'address': 'غرب غزة',
            },
            content_type='application/json',
        )
        self.order = Order.objects.get(code=response.json()['code'])

    def test_the_public_url_uses_the_token_and_not_the_short_code(self):
        url = reverse('restaurant:order_detail', args=[self.order.token])
        self.assertIn(self.order.token, url)
        self.assertNotIn(self.order.code, url)

    def test_guessing_the_short_code_does_not_open_the_order(self):
        response = self.client.get(f'/o/{self.order.code}/')
        self.assertEqual(response.status_code, 404)

    def test_the_token_is_long_enough_to_resist_guessing(self):
        self.assertGreaterEqual(len(self.order.token), 16)

    def test_tokens_differ_between_orders(self):
        second = Order.objects.create()
        self.assertNotEqual(self.order.token, second.token)

    def test_the_customer_details_are_only_reachable_with_the_token(self):
        response = self.client.get(reverse('restaurant:order_detail', args=[self.order.token]))
        self.assertContains(response, 'أحمد')
        self.assertContains(response, 'غرب غزة')

    def test_robots_keeps_order_pages_out_of_search(self):
        response = self.client.get(reverse('restaurant:robots'))
        self.assertContains(response, 'Disallow: /o/')

    def test_the_order_page_asks_not_to_be_indexed(self):
        response = self.client.get(reverse('restaurant:order_detail', args=[self.order.token]))
        self.assertContains(response, 'noindex')
