# عقد الوظائف — Functional Parity

هذا المستند هو **العقد المرجعي** لمشروع فرايز ستيشن. كل وظيفة موثقة هنا كانت تعمل
في خط الأساس المُتحقَّق منه (الكوميت `e254205`، 137 اختبارًا ناجحًا)، ويجب أن تبقى
تعمل بالسلوك نفسه بعد إعادة الهوية.

**قاعدة الاستخدام:** أي تغيير في المظهر يُقاس مقابل عمود «السلوك المتوقع بعد».
إذا اختلف السلوك — لا المظهر — فهذا انحدار (regression) يجب إصلاحه، لا اختبار يجب تعديله.

## مفتاح الحالة

| الرمز | المعنى |
|---|---|
| ⬜ | لم تُنفَّذ مرحلة الرِّبراند لهذه الوظيفة بعد |
| 🔁 | قيد التنفيذ |
| ✅ | نُفِّذت وتم التحقق منها بعد الرِّبراند |
| ⚠️ | نُفِّذت مع ملاحظة أو قيد مذكور |

## قاعدة عامة تسري على كل الجدول

**السلوك المتوقع بعد التعديل = السلوك قبل التعديل، حرفيًا**، ما لم يُذكر خلاف ذلك
صراحة في صف الوظيفة. التغيير المسموح هو: الألوان، الخطوط، المسافات، الظلال،
الأيقونات، الصور، ونصوص العلامة التجارية. غير المسموح: المسارات، أسماء الحقول،
`id`، `data-*`، مفاتيح JSON، أسماء صلاحيات، منطق التسعير، أو آلية التوكن.

---

## 1. الواجهة العامة

| # | الوظيفة | المسار | الملفات المسؤولة | السلوك قبل | التغيير المسموح بعد | حالات النجاح | حالات الخطأ | الصلاحيات | اختبار الإثبات | الحالة |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | الصفحة الرئيسية | `GET /` | `views.home`, `templates/restaurant/home.html` | تعرض Hero والأقسام حسب مفاتيح `show_*` | مظهر فقط | 200 وكل الأقسام المفعّلة ظاهرة | قسم مخفي لا يُصيّر إطلاقًا | عام | `test_home_page_loads` | ⬜ |
| F2 | صفحة القائمة الكاملة | `GET /menu/` | `views.menu_page`, `menu.html` | كتالوج كامل + بحث + فلترة + إظهار المزيد | مظهر فقط | 200 وكل الأصناف المتاحة موجودة في DOM | لا أصناف ← `#filter-empty` | عام | `test_standalone_menu_uses_the_live_catalog_and_cart` | ⬜ |
| F3 | العربية RTL | `?lang=ar` | `base.html:3` | `<html lang="ar" dir="rtl">` | مظهر فقط | الاتجاه rtl والخط Cairo | — | عام | `test_page_direction_matches_the_selected_language` | ⬜ |
| F4 | الإنجليزية LTR | `?lang=en` | `base.html:3`, `style.css` | `<html lang="en" dir="ltr">` والخط Montserrat | مظهر فقط | كل النصوص إنجليزية | — | عام | `test_english_page_uses_english_menu_content` | ⬜ |
| F5 | حفظ اللغة | `?lang=` | `views._language` | تُحفظ في `session['site_language']` وتدوم | لا شيء | التنقل يحافظ على اللغة | قيمة غير `ar`/`en` تُتجاهل | عام | `test_language_switch_is_saved_in_session` | ⬜ |
| F6 | اللغة تبقى على صفحة القائمة | `/menu/?lang=` | `base.html:102` | مبدّل اللغة يشير إلى `menu` لا `home`، ويحافظ على `category` | مظهر فقط | البقاء على `/menu/` | — | عام | `test_menu_language_switch_stays_on_the_menu_page` | ⬜ |
| F7 | قائمة الهاتف | كل الصفحات ≤820px | `base.html:74-98`, `main.js:388-423`, `style.css:486-525` | زر `.nav-toggle` يبدّل `.main-nav.open` + `body.nav-open`؛ الأيقونة تتبدل بين `menu` و`x` عبر `[aria-expanded="true"]`؛ احتياطي نصي `☰`/`×` قبل تحميل الأيقونات | مظهر فقط — **يُمنع تغيير `aria-expanded` أو أسماء الأصناف** | تفتح وتغلق؛ `aria-label` يتبدّل بين `data-open-label` و`data-close-label` | فوق 820px تُغلق قسرًا و`aria-hidden` يُزال | عام | يدوي (م14) + فحص DOM | ⬜ |
| F8 | إغلاق القائمة بالنقر خارجها | ≤820px | `main.js:415-419` | نقرة خارج `.main-nav` و`.nav-toggle` تُغلق | لا شيء | تُغلق | — | عام | يدوي | ⬜ |
| F9 | إغلاق القائمة بـ Escape | ≤820px | `main.js:628-631` | تُغلق ويعود التركيز إلى `.nav-toggle` | لا شيء | التركيز يعود للزر | — | عام | يدوي | ⬜ |
| F10 | القائمة تُغلق عند تغيير المقاس/الاتجاه | — | `main.js:420-422` | `matchMedia change` + `orientationchange` ← إغلاق | لا شيء | لا تبقى مفتوحة على سطح المكتب | — | عام | يدوي | ⬜ |
| F11 | تمييز رابط التنقل النشط | `/` | `main.js:544-572` | يتتبع القسم الذي بلغ الهيدر عبر `requestAnimationFrame` | مظهر فقط | `aria-current="location"` على رابط واحد | لا أقسام ← لا شيء | عام | `test_main_navigation_follows_the_home_page_section_order` | ⬜ |
| F12 | حالة الهيدر عند التمرير | كل الصفحات | `main.js:426-429` | `.scrolled` بعد 18px | مظهر فقط | يتقلص ويغمق | — | عام | يدوي | ⬜ |
| F13 | البحث في القائمة | `/menu/` | `main.js:522-525`, `#menu-search` | يطابق `data-search` (اسم عربي/إنجليزي + وصفان)؛ الكتابة تُرجع الفلتر إلى `all` | مظهر فقط | البحث الفارغ يعيد الفلتر السابق | لا تطابق ← `#filter-empty` | عام | `test_standalone_menu_...` | ⬜ |
| F14 | فلترة التصنيفات | `/`, `/menu/` | `main.js:445-527`, `[data-filter]` | تُظهر `.menu-card[data-category]` المطابقة، تحدّث `#active-filter-label` و`#visible-menu-count` و`aria-pressed` | مظهر فقط | العدّادات صحيحة | تصنيف فارغ ← `#filter-empty` | عام | `test_menu_category_query_marks_the_requested_category_active` | ⬜ |
| F15 | فلترة عبر رابط | `/menu/?category=<slug>` | `views.menu_page:103-108` | slug غير موجود يسقط إلى `all` | لا شيء | الزر المطابق `active` | slug مجهول ← `all` بلا خطأ | عام | نفس الاختبار أعلاه | ⬜ |
| F16 | إظهار المزيد | `/menu/` | `main.js:516-521`, `#menu-load-more`, `data-page-size="6"` | يزيد الحد 6 كل ضغطة، يحدّث `#remaining-menu-count`، ينقل التركيز لآخر بطاقة | مظهر فقط — **`data-page-size` يبقى على `#menu-grid`** | الزر يختفي عند النفاد | 0 متبقٍ ← `hidden` | عام | يدوي | ⬜ |
| F17 | الأكثر طلبًا | `/`, `/menu/` | `views._best_sellers` | مجموع `OrderLine.quantity` مستثنيًا الطلبات الملغاة، أعلى 4 | مظهر فقط | يجمع الأونلاين والكاشير | 0 طلبات ← القسم لا يظهر | عام | `test_best_sellers_use_saved_online_and_cashier_order_quantities` | ⬜ |
| F18 | العروض | `/` | `home.html:165`, `Offer` | بطاقات بأزرار `js-add-item` بمعرّف `offer-<id>` | مظهر فقط — **صيغة المعرّف تبقى** | زر الطلب موجود لكل عرض | لا عروض ← القسم مخفي | عام | `test_offers_have_order_buttons` | ⬜ |
| F19 | الخدمات | `/` | `home.html:201`, `Service` | بطاقات بأيقونات Lucide من `lucide_icon` | مظهر فقط | تظهر حسب `display_order` | `show_services=False` ← مخفي | عام | تصيير الصفحة | ⬜ |
| F20 | التقييمات + الأسهم | `/` | `home.html:268`, `main.js:529-542` | الأسهم تدوّر عناصر `.reviews-track` بـ append/prepend | مظهر فقط | التدوير يعمل في الاتجاهين | لا تقييمات ← مخفي | عام | تصيير الصفحة | ⬜ |
| F21 | FAQ أكورديون | `/` | `main.js:574-588` | فتح واحد يغلق الباقي؛ `aria-expanded` و`aria-hidden` يتزامنان | مظهر فقط | عنصر واحد مفتوح كحد أقصى | لا أسئلة ← مخفي | عام | تصيير الصفحة | ⬜ |
| F22 | المحتوى الاجتماعي | `/` | `views._home_context:76`, `home.html:311` | يستثني صور `/demo/` بلا صورة مرفوعة؛ منشور بلا رابط لا يصبح رابطًا ميتًا | مظهر فقط | الروابط تعمل | بلا `post_url` ← ليس `<a>` | عام | `test_social_post_without_url_is_not_a_dead_link` | ⬜ |
| F23 | إظهار/إخفاء الأقسام | لوحة الإعدادات | `RestaurantSettings.show_*` (9 مفاتيح) | إخفاء القسم يخفي أيضًا رابط التنقل وفلاتره | لا شيء | لا روابط ميتة | — | عام (القراءة) | `test_hiding_menu_also_hides_dead_category_filters_and_nav_link` · `test_about_section_can_be_hidden` | ⬜ |
| F24 | رابط QR للقائمة من الرئيسية | `/` | `home.html` | زر واضح إلى `/menu/` | مظهر فقط | الرابط موجود | — | عام | `test_homepage_has_a_clear_link_to_the_qr_menu` | ⬜ |
| F25 | روابط التواصل الاجتماعي | `/` | `home.html:390`, `partials/icon-*.html` | أزرار موسومة تشير لملفات إنستغرام/فيسبوك | مظهر فقط | تفتح الروابط المضبوطة | رابط فارغ ← الزر لا يظهر | عام | `test_social_title_and_branded_buttons_link_to_social_profiles` | ⬜ |
| F26 | هاتف بلا محارف اتجاه خفية | `/` | `models.display_phone`, `tel_phone` | تُزال محارف الفئة `Cf` من الرقم المنسوخ | لا شيء | `tel:` صالح للاتصال | — | عام | `test_phone_links_strip_invisible_direction_controls` | ⬜ |
| F27 | لا سكربتات CDN | كل الصفحات | `base.html` | كل JS محلي (`lucide-slim.js`, `main.js`) | **لا يجوز إدخال CDN لـ JS** | لا `<script src="http…">` | — | عام | `test_no_external_cdn_scripts` | ⬜ |
| F28 | حركة مخفّضة | كل الصفحات | `main.js:600,616`, `style.css:462` | `prefers-reduced-motion` يعطّل الكشف عند التمرير والبارالاكس | **يجب أن يغطي أي حركة جديدة** | لا حركة عند التفعيل | — | عام | يدوي (م14) | ⬜ |
| F29 | صفحتا 404 و500 | — | `templates/404.html`, `500.html` | صفحتان مخصصتان | مظهر فقط | تظهران بدل الافتراضي | — | عام | يدوي | ⬜ |

---

## 2. السلة والطلبات

| # | الوظيفة | المسار | الملفات | السلوك قبل | التغيير المسموح | حالات النجاح | حالات الخطأ | الصلاحيات | اختبار الإثبات | الحالة |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | إضافة صنف | كل الصفحات | `main.js:234-261`, `.js-add-item` | يقرأ `data-id` `data-name-ar` `data-name-en` `data-price`؛ التكرار يزيد الكمية بحد 99؛ اهتزاز + وميض + إشعار | مظهر فقط — **`data-*` والصنف `.js-add-item` يبقيان** | يظهر في الدرج فورًا | — | عام | `test_standalone_menu_...` | ⬜ |
| C2 | إضافة عرض | `/`, `/menu/` | `main.js:192-209` | `data-offer="true"` + `data-price-text-ar/en`؛ السعر النصي إن كان رقمًا صافيًا يُعامل كمُسعَّر، وإلا `priced:false` | لا شيء | العرض يدخل السلة | نص غير رقمي ← بلا سعر | عام | `test_an_offer_is_quoted_not_computed` | ⬜ |
| C3 | تغيير الكمية | درج السلة | `main.js:263-273`, `[data-cart-action]` | `increase` (≤99) / `decrease` (≥1) | مظهر فقط | الإجمالي يتحدث | — | عام | يدوي | ⬜ |
| C4 | حذف صنف | درج السلة | `main.js:271` | `data-cart-action="remove"` | مظهر فقط | يُزال ويُحفظ | — | عام | يدوي | ⬜ |
| C5 | مسح السلة | `#clear-cart` | `main.js:276-283` | `window.confirm` قبل المسح | مظهر فقط | تُفرغ بعد التأكيد | إلغاء ← لا شيء | عام | يدوي | ⬜ |
| C6 | Local Storage | المتصفح | `main.js:7,36-54` | مفتاح `fries-station-cart`؛ كل سطر يحمل `itemId` و`sizeId` | — | تدوم بعد إعادة التحميل، والحجم معها | تخزين معطّل ← السلة تعمل بلا حفظ؛ حجم اختفى من القائمة ← يُسقط السطر | عام | يدوي | ✅ |
| C7 | تنظيف السلة المخزّنة | التحميل | `main.js:39-51` | كل حقل يُجبَر على نوعه؛ الكمية تُقصّ إلى 1..99؛ عنصر بلا `id` أو اسم يُسقط | لا شيء | JSON تالف ← سلة فارغة لا انهيار | — | عام | يدوي | ⬜ |
| C8 | مزامنة السلة مع الصفحة | التحميل | `main.js:211-217` | صنف لم يعد له زر في الصفحة يُحذف؛ الأسماء والأسعار تُحدَّث من DOM | لا شيء | صنف محذوف يختفي من السلة | — | عام | يدوي | ⬜ |
| C9 | الإجمالي التقريبي | `#cart-total` | `main.js:158-161` | يجمع المُسعَّر فقط؛ يُنبَّه لوجود عناصر بلا سعر | مظهر فقط | الرقم مطابق | — | عام | يدوي | ⬜ |
| C10 | تحليل الأسعار متعدد الأرقام | — | `main.js:13-34` | يتعامل مع الأرقام العربية `٠-٩` والفارسية `۰-۹` والفاصلة العربية `٫` | لا شيء | الأرقام العربية تُحسب | قيمة غير صالحة ← 0 | عام | يدوي | ⬜ |
| C11 | فتح الدرج | `.js-open-cart` | `main.js:90-107` | يغلق قائمة الهاتف، يحفظ التركيز السابق، يضع `inert` على كل أبناء `body` عدا الدرج، ويركّز أول عنصر | مظهر فقط | خلفية غير قابلة للتركيز | لا درج ← لا شيء | عام | يدوي | ⬜ |
| C12 | إغلاق الدرج | `.js-close-cart` / خلفية | `main.js:109-120` | يعيد `inert` ويعيد التركيز إلى العنصر السابق | مظهر فقط | التركيز يعود | — | عام | يدوي | ⬜ |
| C13 | Escape يغلق الدرج | — | `main.js:627` | الأولوية للدرج ثم لقائمة الهاتف | لا شيء | يُغلق | — | عام | يدوي | ⬜ |
| C14 | Focus trap | الدرج | `main.js:632-644` | Tab / Shift+Tab يدوران داخل الدرج فقط | **يجب أن يبقى بعد إعادة التصميم** | لا خروج بالتركيز | لا عناصر ← لا حبس | عام | يدوي (م14) | ⬜ |
| C15 | الدرج يصمد أمام إضافات المتصفح | — | `main.js:71-75` | يُبحث عن `.order-drawer` كسولًا عند كل استخدام | لا شيء | يعمل بعد استبدال DOM | — | عام | يدوي | ⬜ |
| C16 | تبديل الاستلام/التوصيل | `input[name="fulfillment"]` | `main.js:139-152` | التوصيل يُظهر `#delivery-fields` ويضع `required` ويركّز الاسم | مظهر فقط — **`name="fulfillment"` والقيمتان `pickup`/`delivery` تبقيان** | الحقول تظهر وتختفي | — | عام | يدوي | ⬜ |
| C17 | تحقق حقول التوصيل (عميل) | الدرج | `main.js:325-336` | اسم + عنوان + هاتف 7..15 رقمًا بلا محارف غريبة؛ التركيز يقفز لأول حقل ناقص | مظهر فقط | لا يُرسل الطلب | رسالة في `#cart-feedback` | عام | يدوي | ⬜ |
| C18 | تحقق حقول التوصيل (خادم) | `POST /order/` | `views_order.py:106-113` | يُعاد التحقق على الخادم — العميل ليس مصدر ثقة | **لا يجوز إضعافه** | 400 عند النقص | JSON `{"error": …}` | عام | `test_delivery_requires_name_phone_and_address` | ⬜ |
| C19 | الاستلام بلا بيانات | `POST /order/` | `views_order.py` | لا يشترط اسمًا ولا هاتفًا | لا شيء | الطلب يُنشأ | — | عام | `test_pickup_does_not_require_contact_details` | ⬜ |
| C20 | **التسعير من قاعدة البيانات** | `POST /order/` | `views_order.py:73-160` | المتصفح يرسل `{id, qty}` فقط؛ أي `price` مُرسل **يُتجاهل** | **ممنوع المساس** | الإجمالي = مجموع أسعار القائمة | — | عام | `test_the_server_prices_the_order_from_the_menu` · `test_a_price_sent_by_the_browser_is_ignored` | ⬜ |
| C20b | **اختيار الحجم** | `/`, `/menu/`, `POST /order/` | `models.MenuItemSize`, `views_order._resolve_price`, `main.js` | جديد بعد خط الأساس | **إضافة** | الحجم المختار يحدد السعر ويُحفظ نسخةً على السطر | حجم غريب أو معطّل أو غائب ← يرجع إلى الأصغر، ولا يتجاوز ما عُرض | عام | `ItemSizePricingTests` (10) | ✅ |
| C21 | لقطة السعر لا مرجع | — | `OrderLine` | الاسم والسعر نسخة وقت الطلب | **ممنوع المساس** | تعديل القائمة لا يغيّر طلبًا قديمًا | حذف الطبق ← الطلب يبقى مقروءًا | — | `test_line_prices_are_a_snapshot_not_a_live_lookup` · `test_deleting_a_dish_keeps_the_order_readable` | ⬜ |
| C22 | دمج المعرّفات المكررة | `POST /order/` | `views_order.py:94` | نفس المعرّف مرتين ← سطر واحد بكمية مجمّعة | لا شيء | سطر واحد | — | عام | `test_repeated_ids_are_merged_rather_than_duplicated` | ⬜ |
| C23 | إسقاط غير المتاح | `POST /order/` | `views_order.py:132` | `is_available=False` يُسقط بصمت | لا شيء | الطلب يتم بالباقي | كله غير متاح ← 409 | عام | `test_an_unavailable_dish_is_dropped` · `test_an_order_of_only_unavailable_dishes_is_refused` | ⬜ |
| C24 | حدود الحجم | `POST /order/` | `views_order.py:27-28` | 40 سطرًا كحد أقصى، الكمية 1..99 | لا شيء | ضمن الحد ← نجاح | تجاوز ← 400 / إسقاط | عام | `test_quantities_outside_the_allowed_range_are_dropped` | ⬜ |
| C25 | رفض المدخلات التالفة | `POST /order/` | `views_order.py:62-71` | JSON غير صالح ← 400؛ سلة فارغة ← 400؛ GET ← 405 | لا شيء | — | رسائل واضحة | عام | `test_malformed_json_is_refused` · `test_an_empty_cart_is_refused` · `test_a_get_is_not_allowed` | ⬜ |
| C26 | **رمز الطلب** | — | `models.Order._new_code` | 4 محارف من أبجدية بلا `I O 0 1`؛ البادئة `B12-` — **تُغيَّر إلى بادئة فرايز ستيشن (م12)** | **تغيير البادئة مسموح ومطلوب؛ الأبجدية والطول يبقيان** | فريد عبر آلاف الطلبات | تصادم متكرر ← رمز أطول | عام | `test_codes_are_unique_across_many_orders` · `test_the_code_avoids_characters_that_are_misread_aloud` | ⬜ |
| C27 | **خصوصية رابط الطلب** | `GET /o/<token>/` | `models.Order.token`, `views_order.order_detail` | `secrets.token_urlsafe(12)` منفصل عن الرمز القصير؛ تخمين الرمز لا يفتح الطلب | **ممنوع المساس** | التوكن الصحيح ← 200 | رمز قصير في المسار ← 404 | من يملك التوكن | `OrderUrlPrivacyTests` (6 اختبارات) | ⬜ |
| C28 | صفحة الطلب للقراءة فقط | `GET /o/<token>/` | `order_detail.html` | تعرض الإجمالي من الخادم؛ الموظف يرى إشارة إدارية لكنه لا يعدّل هنا | مظهر فقط | الإجمالي مطابق | توكن مجهول ← 404 | من يملك التوكن | `test_the_order_page_shows_the_server_total` | ⬜ |
| C29 | منع فهرسة صفحة الطلب | — | `order_detail.html`, `robots.txt` | `noindex` + `Disallow: /o/` | لا شيء | خارج محركات البحث | — | — | `test_the_order_page_asks_not_to_be_indexed` · `test_robots_keeps_order_pages_out_of_search` | ⬜ |
| C30 | رسالة واتساب | بعد الطلب | `views_order._whatsapp_message` | 4 أسطر: تحية، رقم الطلب، «عرض الطلب:»، ثم **الرابط وحده على سطره** بلا أي محرف سابق (وإلا لا تصبح قابلة للنقر) | **النص التسويقي يتغير؛ بنية الأسطر تبقى** | الرابط قابل للنقر | لا رقم واتساب ← يُعرض رقم الطلب للعميل | عام | `test_the_whatsapp_message_carries_the_code_and_no_prices` · `test_the_link_sits_alone_so_whatsapp_makes_it_tappable` · `test_nothing_precedes_the_link_on_its_line` | ⬜ |
| C31 | الانتقال إلى واتساب | بعد الطلب | `main.js:305-309` | `location.href` لا `window.open` (لانتهاء صلاحية تفعيل المستخدم) | لا شيء | يفتح محادثة المطعم | لا رقم ← رسالة بالرمز | عام | يدوي | ⬜ |
| C32 | تفريغ السلة بعد النجاح | — | `main.js:368-370` | تُفرَّغ **قبل** الانتقال | لا شيء | لا طلب مكرر | — | عام | يدوي | ⬜ |
| C33 | إيصال PNG | `GET /o/<token>/receipt.png` | `receipt.py` | يُرسم على الخادم؛ العربية تُشكَّل بـ `arabic-reshaper` + `python-bidi` بخط **IBM Plex Sans Arabic** | **الألوان والتخطيط فقط — الخط لا يُستبدل** | `Content-Type: image/png` | فشل الرسم ← 404 مسجَّل | من يملك التوكن | `test_the_receipt_renders_as_a_png` · `test_every_glyph_the_receipt_needs_exists_in_the_bundled_font` | ⬜ |
| C34 | الإيصال خارج الفهرسة | — | `views_order.order_receipt` | `X-Robots-Tag: noindex` + `Cache-Control: private` | لا شيء | خاص | — | من يملك التوكن | `test_the_receipt_is_kept_out_of_search_engines` | ⬜ |
| C35 | Rate Limiting للطلبات | `POST /order/` | `views_order.py:33-41` | 12 طلبًا/10 دقائق لكل عنوان | **لا يجوز رفعه** | ضمن الحد ← نجاح | تجاوز ← 429 | عام | `test_the_endpoint_is_rate_limited` | ⬜ |
| C36 | مقاومة انتحال IP | — | `views._client_address` | `X-Forwarded-For` يُقرأ بقدر `TRUSTED_PROXY_HOPS` فقط | **ممنوع المساس** | خلف وكيل موثوق يعمل | ترويسة منتحلة ← لا تجاوز | عام | `test_spoofed_forwarded_for_does_not_bypass_rate_limit` | ⬜ |
| C37 | CSRF على الطلب | `POST /order/` | `base.html:65`, `main.js:289` | نموذج مخفي `#csrf-holder` يزوّد `X-CSRFToken` | **`#csrf-holder` يبقى** | الطلب يمر | بلا توكن ← 403 | عام | مجموعة اختبارات الطلب | ⬜ |

---

## 3. الحجز

| # | الوظيفة | المسار | الملفات | السلوك قبل | التغيير المسموح | حالات النجاح | حالات الخطأ | الصلاحيات | اختبار الإثبات | الحالة |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | إنشاء حجز | `POST /reservation/` | `views.create_reservation`, `forms.ReservationForm` | يحفظ ثم يحوّل إلى واتساب برسالة مفصّلة | نص الرسالة فقط | يُحفظ + تحويل | — | عام | `test_valid_reservation_is_saved_and_redirects_to_whatsapp` | ⬜ |
| R2 | تحقق الحقول | — | `ReservationForm` | `full_name` `phone` `date` `time` `guests` مطلوبة؛ رسائل الخطأ تتبع اللغة | نص الرسائل فقط | — | نموذج غير صالح ← لا حفظ + إعادة توجيه `#contact` | عام | `test_invalid_reservation_is_not_saved` | ⬜ |
| R3 | حفظ المسودة عند الخطأ | — | `views.py:164-166` | القيم تُحفظ في الجلسة وتُعاد للنموذج | لا شيء | العميل لا يعيد الكتابة | — | عام | `test_past_reservation_is_rejected_and_values_are_preserved` | ⬜ |
| R4 | تحقق الهاتف | — | `forms.clean_phone` | يسمح `+ - ( )` والمسافات فقط؛ 7..15 رقمًا؛ يُخزَّن أرقامًا صافية | لا شيء | رقم صالح ← حفظ | حروف ← رفض ولو كفت الأرقام | عام | `test_invalid_reservation_phone_is_rejected` · `test_phone_with_letters_is_rejected_even_when_it_has_enough_digits` | ⬜ |
| R5 | منع الماضي (تاريخ) | — | `forms.clean_date` | تاريخ سابق مرفوض | لا شيء | اليوم فما بعد | — | عام | `test_past_reservation_is_rejected...` | ⬜ |
| R6 | منع الماضي (وقت اليوم) | — | `forms.clean` | وقت مضى اليوم مرفوض | لا شيء | — | خطأ على حقل `time` | عام | `test_past_reservation_is_rejected...` | ⬜ |
| R7 | أقصى مدة مسبقة | — | `forms.clean_date` | `max_reservation_days_ahead` (افتراضي 90) | لا شيء | داخل النافذة | خارجها ← رفض برسالة تذكر العدد | عام | `test_reservation_beyond_configured_advance_window_is_rejected` | ⬜ |
| R8 | حد أدنى للتاريخ في الواجهة | `/` | `forms.__init__` | `min`/`max` على حقل التاريخ | لا شيء | منتقي التاريخ محدود | — | عام | `test_reservation_date_has_today_as_minimum` | ⬜ |
| R9 | ساعات الاستقبال | — | `forms.clean` | يدعم المدى العابر لمنتصف الليل (08:00 ← 02:00) | لا شيء | داخل الساعات | خارجها ← رسالة بالساعات | عام | تحقق النموذج | ⬜ |
| R10 | فواصل المواعيد | — | `forms.clean` | الوقت يجب أن يقبل القسمة على `reservation_slot_minutes` | لا شيء | 15/30/60 | غير مطابق ← رفض | عام | تحقق النموذج | ⬜ |
| R11 | سعة الفترة | — | `forms.clean` | `max_reservations_per_slot` (افتراضي 6) للحالات النشطة | لا شيء | ضمن السعة | ممتلئة ← رفض | عام | `test_full_reservation_slot_is_rejected` | ⬜ |
| R12 | منع التكرار | `POST /reservation/` | `views.py:187-198` | نفس الهاتف + التاريخ + الوقت بحالة نشطة ← رفض، داخل `select_for_update` | لا شيء | حجز واحد | مكرر ← رسالة | عام | `test_duplicate_reservation_is_not_created` | ⬜ |
| R13 | رقم واتساب مطلوب | — | `views.py:170-176` | بلا رقم مضبوط لا يُحفظ الحجز إطلاقًا | لا شيء | — | رسالة «رقم واتساب غير مضبوط» | عام | `test_reservation_is_not_saved_without_whatsapp_number` | ⬜ |
| R14 | Rate Limiting للحجز | `POST /reservation/` | `views.py:140-149` | 5/10 دقائق؛ ترويسة `Retry-After: 600` | **لا يجوز رفعه** | ضمن الحد | تجاوز ← 429 | عام | `test_reservation_endpoint_is_rate_limited` | ⬜ |
| R15 | إشعار بريد اختياري | — | `views._notify_new_reservation` | يُرسل فقط عند ضبط `EMAIL_HOST` و`RESERVATION_NOTIFY_EMAIL`؛ `fail_silently` | لا شيء | يصل الإشعار | فشل ← يُسجَّل ولا يكسر الحجز | — | تشغيلي | ⬜ |
| R16 | حالات الحجز | — | `Reservation.STATUS_CHOICES` | `new` `contacted` `confirmed` `cancelled` | **القيم تبقى؛ التسميات قابلة للتغيير** | التغيير يُسجَّل | حالة مجهولة ← رفض | `change_reservation` | `test_an_unknown_status_is_rejected` | ⬜ |
| R17 | تعطيل زر الإرسال | `/` | `main.js:590-596` | يُعطَّل عند الإرسال لمنع الازدواج | مظهر فقط | إرسال واحد | — | عام | يدوي | ⬜ |

---

## 4. الإدارة والتشغيل

| # | الوظيفة | المسار | الملفات | السلوك قبل | التغيير المسموح | حالات النجاح | حالات الخطأ | الصلاحيات | اختبار الإثبات | الحالة |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | حماية اللوحة | `/dashboard/*` | `@staff_member_required` | زائر ← تحويل لتسجيل دخول الإدارة؛ مستخدم غير موظف ← رفض | لا شيء | الموظف يدخل | غير مصرّح ← تحويل/رفض | staff | `DashboardAccessTests` (5) | ⬜ |
| A2 | CRM — بناء العملاء | `/dashboard/` | `crm.build_customers` | لا جدول عملاء؛ يُشتق من الحجوزات مجمّعًا بأرقام الهاتف الصافية | **ممنوع تحويله لجدول** | نفس الرقم بصيغ مختلفة = عميل واحد | حجز بلا هاتف صالح ← يُتخطى | staff | `CustomerRecordTests` (12) | ⬜ |
| A3 | الشرائح | `/dashboard/` | `crm._segment_for` | `new` (1) · `regular` (2–4) · `vip` (≥5) · `lapsed` (≥2 زيارة وغاب >60 يومًا) | **التسميات قابلة للتغيير؛ العتبات تبقى** | التصنيف صحيح | زائر لمرة واحدة قديم ليس `lapsed` | staff | 5 اختبارات في `CustomerRecordTests` | ⬜ |
| A4 | الملغى ليس زيارة | — | `crm.build_customers` | `cancelled` يُعدّ إلغاءً لا زيارة | لا شيء | — | — | staff | `test_a_cancelled_booking_is_not_a_visit` | ⬜ |
| A5 | المستقبلي ليس زيارة | — | `crm.build_customers` | حجز لاحق ← `upcoming` | لا شيء | — | — | staff | `test_a_future_booking_counts_as_upcoming_not_as_a_visit` | ⬜ |
| A6 | إيقاع 12 شهرًا | `/dashboard/` | `crm._visit_rhythm` | 12 خلية بأربعة مستويات، الأحدث آخرًا | مظهر فقط | تنتهي بالشهر الحالي | — | staff | `test_the_rhythm_covers_twelve_months_ending_this_month` | ⬜ |
| A7 | البحث والفرز | `/dashboard/?q=&segment=&sort=` | `crm.filter_customers`, `sort_customers` | بحث بالاسم أو أي جزء من الرقم (يتجاهل الشرطات)؛ فرز `last`/`visits`/`covers`/`name` | مظهر فقط | النتائج صحيحة | فرز/شريحة مجهولة ← تراجع آمن | staff | `CustomerFilterTests` (6) + `test_an_unknown_sort_falls_back_instead_of_erroring` | ⬜ |
| A8 | حجوزات الليلة | `/dashboard/#tonight` | `crm.tonight` | كل حجز موسوم بمدى معرفة الضيف؛ اليوم لا يُحتسب زيارة سابقة | مظهر فقط | «أول زيارة» صحيحة | الملغاة لا تظهر | staff | `TonightTests` (3) | ⬜ |
| A9 | تصريف الأعداد العربي | `/dashboard/` | `crm.count_ar`, `_relative_day_phrase` | `زيارتان` لا `2 زيارة`؛ `قبل يومين` بالمجرور | **يجب الحفاظ عليه في أي نص جديد** | العبارة سليمة | — | staff | `RelativeDatePhraseTests` (2) | ⬜ |
| A10 | تغيير حالة الحجز | `POST /dashboard/reservations/<pk>/status/` | `views_dashboard` | POST فقط؛ يعود لنفس القائمة المفلترة عبر `CARRIED_FILTERS` | مظهر فقط | الحالة تتغير برسالة | GET ← 405 · حالة مجهولة ← رفض | `change_reservation` | `DashboardStatusActionTests` (5) | ⬜ |
| A11 | لوحة الأقسام — عرض | `GET /dashboard/<slug>/` | `views_panel.section_list`, `panel.SECTIONS` | 10 أقسام؛ جدول + بحث + ترقيم 25/صفحة | مظهر فقط — **`slug` كل قسم يبقى** | السجلات تظهر | slug مجهول ← 404 | `view_<model>` | `ControlPanelTests` (13) | ⬜ |
| A12 | إضافة وتعديل | `/dashboard/<slug>/new/` و `/<pk>/` | `views_panel.section_form` | `modelform_factory` + منتقيات أصلية للتاريخ/الوقت/اللون | مظهر فقط | يُحفظ برسالة | غير صالح ← إعادة عرض بلا حفظ | `add_` / `change_` | 3 اختبارات | ⬜ |
| A13 | تبديل سريع | `POST /dashboard/<slug>/<pk>/toggle/` | `views_panel.section_toggle` | الحقل يجب أن يكون ضمن `section['toggles']` | لا شيء | يُقلب | حقل خارج القائمة ← `PermissionDenied` | `change_<model>` | `test_toggling_a_field_outside_the_allowlist_is_refused` | ⬜ |
| A14 | حذف | `POST /dashboard/<slug>/<pk>/delete/` | `views_panel.section_delete` | POST فقط؛ قسم فيه أطباق محمي بـ `PROTECT` والرسالة تشرح | نص الرسالة فقط | يُحذف | مرتبط ← رسالة واضحة لا انهيار | `delete_<model>` | `test_deleting_a_category_that_still_has_dishes_is_explained` | ⬜ |
| A15 | الطلبات في اللوحة | `/dashboard/orders/` | `panel.SECTIONS['orders']` | `can_add: False`؛ الحقول القابلة للتعديل: الحالة، الاستلام، الاسم، الهاتف، العنوان، الملاحظات — **لا الإجمالي** | **ممنوع إضافة `total` للنموذج** | الحالة تتغير | محاولة تعديل الإجمالي ← لا أثر | `change_order` | `test_staff_cannot_rewrite_the_total_from_the_panel` | ⬜ |
| A16 | الشريط الجانبي يتبع الصلاحيات | كل اللوحات | `panel.nav` | لا يعرض إلا الأقسام المسموحة | مظهر فقط | القائمة مطابقة للصلاحيات | بلا صلاحيات ← قائمة فارغة لا خطأ | staff | `test_the_sidebar_only_lists_permitted_sections` | ⬜ |
| A17 | إعدادات الموقع | `/dashboard/settings/` | `views_panel.site_settings`, `panel.SETTINGS_GROUPS` | سجل مفرد (pk=1)، حقول مجمّعة بترتيب قراءة الصفحة | **مجموعات الحقول قابلة لإعادة التنظيم** | يُحفظ | بلا الصلاحية ← رفض | `change_restaurantsettings` | `test_the_settings_page_saves_a_change` · `test_settings_needs_its_own_permission` | ⬜ |
| A18 | تحقق تباين الألوان | لوحة الإعدادات | `admin.RestaurantSettingsAdminForm.clean` | يرفض لونًا نسبة تباينه <4.5 مقابل مرجع؛ **المراجع الحالية مبنية على واجهة داكنة** | **تُحدَّث المراجع لتناسب سطح فاتح — والفحص يبقى بنفس القوة (4.5:1)** | لون مقبول ← حفظ | ضعيف ← خطأ على الحقل | `change_restaurantsettings` | `test_the_settings_page_saves_a_change` | ⬜ |
| A19 | الكاشير — الوصول | `/dashboard/cashier/` | `views_cashier.cashier` | يتطلب `add_order` فوق `staff` | لا شيء | الصفحة تفتح | بلا الصلاحية ← رفض | `add_order` | `test_cashier_page_requires_add_order_permission` | ⬜ |
| A20 | الكاشير — إنشاء طلب | `POST /dashboard/cashier/` | `views_cashier` | `source='cashier'`, `fulfillment='dine_in'`, `status='confirmed'`؛ **الأسعار من قاعدة البيانات**؛ يسجّل الموظف | **ممنوع المساس بالتسعير** | يُحفظ ويحوّل بـ `?created=<token>` | عدد زبائن خارج 1..100 أو سلة فارغة ← 400 مع الاحتفاظ بالمدخلات | `add_order` | `test_cashier_order_is_saved_and_priced_from_the_database` | ⬜ |
| A21 | إحصاءات اليوم | `/dashboard/cashier/` | `views_cashier._today_stats` | زبائن داخل/خارج + عدد الطلبات + المبيعات، مستثنيًا الملغاة | مظهر فقط | الأرقام مطابقة | لا طلبات ← أصفار | `add_order` | `test_cashier_dashboard_counts_inside_and_online_customers` | ⬜ |
| A22 | Django Admin — الإحصاءات | `/admin/` | `templatetags/b12_admin.py`, `templates/admin/index.html` | 4 بطاقات: الليلة، تنتظر ردًا، العملاء، الأطباق — **الملف والوسم يُعاد تسميتهما (م12)** | **إعادة التسمية مسموحة ومطلوبة** | البطاقات تظهر | موظف بلا صلاحيات ← صفحة تعمل | staff | `AdminSkinTests` (5) | ⬜ |
| A23 | Admin — منع إنشاء طلب يدويًا | `/admin/` | `OrderAdmin.has_add_permission` | `False` — الطلبات تُنشأ من الموقع أو الكاشير فقط | **ممنوع المساس** | — | — | — | فحص الإدارة | ⬜ |
| A24 | Admin — أسطر الطلب للقراءة | `/admin/` | `OrderLineInline` | كل الحقول `readonly`، لا إضافة ولا حذف | **ممنوع المساس** | — | — | — | فحص الإدارة | ⬜ |
| A25 | Admin — الإعدادات سجل واحد | `/admin/` | `RestaurantSettingsAdmin` | لا إضافة إن وُجد سجل، ولا حذف إطلاقًا | لا شيء | — | — | — | فحص الإدارة | ⬜ |
| A26 | صلاحيات Django القياسية | كل اللوحات | `panel.perm` | `<app>.<action>_<model>` بلا نظام أدوار مخصص | **ممنوع استبداله** | الأدوار الحالية تستمر | — | — | `ControlPanelPermissionTests` (6) | ⬜ |
| A27 | جلسة واحدة للإدارة واللوحة | — | `staff_member_required` | الخروج من الإدارة يُخرج من اللوحة | لا شيء | — | — | staff | `DashboardAccessTests` | ⬜ |

---

## 5. SEO والبنية التحتية

| # | الوظيفة | المسار | الملفات | السلوك قبل | التغيير المسموح | اختبار الإثبات | الحالة |
|---|---|---|---|---|---|---|---|
| S1 | وسوم SEO | كل الصفحات | `base.html:7-23` | `description`, `og:*`, `canonical`, `hreflang` ar/en/x-default | المحتوى النصي | `test_seo_head_tags_are_present` | ⬜ |
| S2 | Schema.org | كل الصفحات | `base.html:24-43` | `@type: Restaurant` مع `servesCuisine` و`address` و`telephone` | **`servesCuisine` يتغير إلى مطبخ فرايز ستيشن** | `test_seo_head_tags_are_present` | ⬜ |
| S3 | صورة المشاركة | — | `views._absolute_media_url` | الرابط المطلق لا يُسبق بالمضيف مرتين | لا شيء | `test_absolute_open_graph_image_url_is_not_prefixed` | ⬜ |
| S4 | robots.txt | `/robots.txt` | `views.robots_txt` | يمنع `/admin/` و`/dashboard/` و`/o/` ويعلن الـsitemap | لا شيء | `test_robots_txt_and_sitemap_xml` · `test_robots_txt_keeps_the_dashboard_out_of_search` | ⬜ |
| S5 | sitemap.xml | `/sitemap.xml` | `views.sitemap_xml` | الرئيسية والقائمة مع بدائل اللغة | لا شيء | `test_robots_txt_and_sitemap_xml` | ⬜ |
| S6 | صور محلية صالحة | لوحة الإعدادات | `models.image_source_validator` | يقبل رابط HTTP(S) أو مسار `/static/` `/media/`؛ يرفض `..` وبيانات الدخول في الرابط | لا شيء | `test_relative_static_image_paths_are_valid_in_admin_forms` | ⬜ |
| S7 | صورة Hero للهاتف | `/` | `models.hero_image_mobile_src` | **مربوط باسم ملف `hero-b12.webp` — يُعمَّم في م9** | **التعميم مطلوب وإلا اختفت النسخة المحمولة بصمت** | يدوي (م14) | ⬜ |
| S8 | ترويسات الأمان | كل الصفحات | `config/settings.py` | `X_FRAME_OPTIONS: DENY`, `SECURE_REFERRER_POLICY`, كوكيز آمنة خارج التطوير | لا شيء | `manage.py check --deploy` | ⬜ |
| S9 | رفض الإقلاع بلا مفتاح سري | — | `settings.py:16-19` | `DEBUG=0` بلا `DJANGO_SECRET_KEY` ← `ImproperlyConfigured` | **ممنوع المساس** | يدوي | ⬜ |

---

## ملحق: العقود التقنية التي لا تُكسر أثناء إعادة التصميم

عناصر يقرأها JavaScript بالاسم. تغيير أي منها يكسر السلة أو الفلترة أو البحث بصمت
دون أن يفشل أي اختبار Python.

### مُعرِّفات `id`
```
#csrf-holder  #cart-items  #cart-empty  #cart-total  #cart-feedback  #clear-cart
#delivery-fields  #order-name  #order-phone  #order-address  #order-notes
#send-whatsapp  #menu-grid  #menu-search  #menu-load-more  #filter-empty
#active-filter-label  #visible-menu-count  #total-menu-count  #remaining-menu-count
#main-nav  #main  #top
```

### أصناف CSS ذات سلوك
```
.js-add-item  .js-open-cart  .js-close-cart  .order-drawer  .nav-toggle  .main-nav
.menu-card  .site-header  .header-whatsapp  .floating-whatsapp  .reviews-track
.review-arrow.next  .review-arrow.prev  .faq-item  .reservation-form  .reveal
.js-parallax  .cart-item  .add-label  .is-hidden  .hidden  .open  .is-open
.scrolled  .added  .cart-pulse  .revealed  .icons-ready
```

### سمات البيانات
```
body[data-lang] [data-currency] [data-whatsapp] [data-order-url]
.js-add-item[data-id] [data-name-ar] [data-name-en] [data-price]
               [data-offer] [data-price-text-ar] [data-price-text-en]
[data-filter] [data-filter-label] [data-clear-search] [data-footer-filter]
.menu-card[data-category] [data-search]
#menu-grid[data-page-size]
[data-cart-action] [data-cart-id]
.js-add-item[data-item]           يربط الزر بمنتقي الحجم في بطاقته
.size-picker input[name=size-<id>] [data-price] [data-size-ar] [data-size-en]
.nav-toggle[data-open-label] [data-close-label] [aria-expanded]
.reservation-form button[data-submit-label]
```

### عقد JSON لنقطة الطلب
```
الطلب:  {items: [{id, size?, qty}], fulfillment, name, phone, address, notes}
الرد:   {code, order_url, receipt_url, whatsapp_url, message}
الخطأ:  {error: "..."}   بحالة 400 / 409 / 429
```

### أسماء أقسام اللوحة (`slug`)
```
orders  reservations  menu  sizes  categories  offers  services  reviews  faq  social  hero
```

### قيم قواعد البيانات المحفوظة
```
Order.status        new confirmed preparing delivered cancelled
Order.fulfillment   pickup delivery dine_in
Order.source        online cashier
Reservation.status  new contacted confirmed cancelled
```

---

## عناصر يجب تغييرها عمدًا (وليست انحدارًا)

| العنصر | من | إلى | المرحلة |
|---|---|---|---|
| مفتاح localStorage | `b12-whatsapp-cart` | `fries-station-cart` | ✅ تم |
| بادئة رمز الطلب | `B12-` | `FS-` عبر `Order.CODE_PREFIX` | ✅ تم |
| ملف ووسم إحصاءات الإدارة | `b12_admin.py` / `b12_admin_stats` | تسمية فرايز ستيشن | 12 |
| مراجع تباين الألوان | مبنية على `#050505` / سطح داكن | مبنية على هوية فرايز ستيشن | 6 و10 |
| `hero_image_mobile_src` | مربوط بـ `hero-b12.webp` | منطق معمَّم | 9 |
| `servesCuisine` | `Middle Eastern, International` | مطبخ فرايز ستيشن | 11 |
| اسم الكاش | `b12-restaurant` | `fries-station` | 12 |
| مجلد الصور | `static/restaurant/img/v3/` | `static/restaurant/img/fries-station/` | 8 |
