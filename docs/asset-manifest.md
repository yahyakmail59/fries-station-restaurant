# Asset Manifest — فرايز ستيشن

كل صورة طعام في هذا المشروع مصدرها صفحة الطلب الرسمية للمطعم على سنبل، بإذن المالك.
لم تُحمَّل أي صورة من مصدر آخر، ولم تُولَّد أي صورة طعام بالذكاء الاصطناعي.

## المعالجة المطبَّقة

تدرّج لوني سينمائي غير مُتلِف على كل صورة، بلا أي تغيير في محتواها:

| الخطوة | القيمة | السبب |
|---|---|---|
| منحنى نغمي على شكل S | كتف محفوظ عند 243 | يرفع الأوساط بلا حرق لمعان الجبن والصوص |
| موازنة بيضاء دافئة | أحمر +6، أخضر +2، أزرق −5 في الأوساط | يوافق «إضاءة دافئة» في دليل الهوية |
| تشبّع | ‎+10٪ | لون غني بلا مبالغة |
| تباين | ‎+6٪ | فصل الطعام عن الخلفية |
| Vignette | ‎16٪، نصف قطر ‎16٪ | تركيز العين على الطبق |
| Unsharp Mask | نصف قطر 1.6، ‎62٪، عتبة 3 | حدّة القرمشة |

**الصور المقصوصة على خلفية بيضاء (كوكاكولا، سبرايت، مياه) تُستثنى من الـVignette**
لأن تعتيم الحواف على الأبيض يبدو كعيب طباعة لا كأسلوب.

## الأصول القديمة المستبدَلة

| الأصل القديم | البديل | الحالة |
|---|---|---|
| `img/v3/*.webp` (20 ملفًا: شاورما، مشاوي، ستيك، سمك، بيتزا، باستا…) | `img/fries-station/menu/*.webp` | حُذف بالكامل |
| `img/b12-logo-clean.jpg` | `img/fries-station/branding/logo.webp` | حُذف |
| `img/apple-touch-icon.png` (شعار B12) | مشتق من شعار فرايز ستيشن | استُبدل |
| `img/favicon.ico` (شعار B12) | مشتق من شعار فرايز ستيشن | استُبدل |
| `output/print/b12-table-menu-qr.png` | — | لم يُنسخ إطلاقًا |

## أصول الهوية

| الملف | المقاس | المصدر |
|---|---|---|
| `branding/logo.webp` | 1024×1024 | مشتق من ملف شعار فرايز ستيشن الرسمي |
| `branding/logo-512.webp` | 512×512 | مشتق من ملف شعار فرايز ستيشن الرسمي |
| `branding/apple-touch-icon.png` | 180×180 | مشتق من ملف شعار فرايز ستيشن الرسمي |
| `branding/og-fries-station.webp` | 1200×630 | مشتق من ملف شعار فرايز ستيشن الرسمي |
| `hero/hero-fries-station.webp` | 1920×822 | قصّة 21:9 من صورة «كرنوش فرايز» |
| `hero/hero-fries-station-960.webp` | 960×411 | قصّة 21:9 من صورة «كرنوش فرايز» |
| `categories/drinks.webp` | 640×853 | صنف من القسم نفسه |
| `categories/fries.webp` | 640×853 | صنف من القسم نفسه |
| `categories/kids.webp` | 640×853 | صنف من القسم نفسه |
| `categories/salad.webp` | 640×853 | صنف من القسم نفسه |
| `categories/sandwiches.webp` | 640×853 | صنف من القسم نفسه |
| `categories/sauces.webp` | 640×853 | صنف من القسم نفسه |
| `categories/stripes.webp` | 640×853 | صنف من القسم نفسه |
| `categories/sweets.webp` | 640×853 | صنف من القسم نفسه |

## صور الأصناف

النص البديل لكل صورة هو اسم الصنف باللغة المعروضة، يولّده القالب تلقائيًا.

| الصنف | English | الملف | المقاس | الحجم | الأصل | الحالة |
|---|---|---|---|---|---|---|
| فرايز | Fries | menu/fries.webp | 960×960 | 97 KB | 1254×1254 | معتمدة |
| بوم فرايز | Boom Fries | — | — | — | 303×267 (شعار) | ناقصة |
| سماش فرايز | Smash Fries | menu/smash-fries.webp | 960×960 | 217 KB | 1254×1254 | معتمدة |
| زنجر فرايز | Zinger Fries | menu/zinger-fries.webp | 960×960 | 183 KB | 1254×1254 | معتمدة |
| بيكاتا فرايز | Piccata Fries | — | — | — | 303×267 (شعار) | ناقصة |
| ناجيتس فرايز | Nuggets Fries | menu/nuggets-fries.webp | 960×960 | 233 KB | 1254×1254 | معتمدة |
| شريمب فرايز | Shrimp Fries | menu/shrimp-fries.webp | 960×960 | 181 KB | 1254×1254 | معتمدة |
| رويال فرايز | Royal Fries | menu/royal-fries.webp | 960×960 | 214 KB | 1254×1254 | معتمدة |
| كلاسيك فرايز | Classic Fries | menu/classic-fries.webp | 960×960 | 287 KB | 1254×1254 | معتمدة |
| جمبري فرايز | Jumbo Fries | — | — | — | 303×267 (شعار) | ناقصة |
| جولد ستربس | Gold Stripes | menu/gold-stripes.webp | 960×960 | 253 KB | 1254×1254 | معتمدة |
| فاير ستربس | Fire Stripes | menu/fire-stripes.webp | 960×960 | 254 KB | 1254×1254 | معتمدة |
| بافلو ستربس | Buffalo Stripes | menu/buffalo-stripes.webp | 960×960 | 234 KB | 1254×1254 | معتمدة |
| وجبة أطفال | Kids Meal | menu/kids-meal.webp | 960×960 | 211 KB | 1254×1254 | معتمدة |
| سموكي ستيشن BBQ | Smoky Station BBQ | menu/smoky-station-bbq.webp | 960×960 | 247 KB | 1254×1254 | معتمدة |
| كرنوش فرايز | Crunch Fries Wrap | menu/crunch-fries.webp | 960×960 | 210 KB | 1254×1254 | معتمدة |
| سماش برجر | Smash Burger | menu/smash-burger.webp | 960×960 | 185 KB | 1254×1254 | معتمدة |
| بوب زنجر | Pop Zinger | menu/pop-zinger.webp | 960×960 | 246 KB | 1254×1254 | معتمدة |
| تشيكن بيكاتا | Chicken Piccata | menu/chicken-piccata.webp | 960×960 | 238 KB | 1254×1254 | معتمدة |
| هامر ستيشن | Hammer Station | menu/hammer-station.webp | 960×960 | 243 KB | 1254×1254 | معتمدة |
| صوص FS | FS Sauce | menu/fs-sauce.webp | 960×960 | 133 KB | 1254×1254 | معتمدة |
| شيدر صوص | Cheddar Sauce | menu/cheddar-sauce.webp | 960×960 | 192 KB | 1254×1254 | معتمدة |
| رانش صوص | Ranch Sauce | menu/ranch-sauce.webp | 960×960 | 156 KB | 1254×1254 | معتمدة |
| بافلو صوص | Buffalo Sauce | menu/buffalo-sauce.webp | 960×960 | 160 KB | 1254×1254 | معتمدة |
| باربيكيو صوص | BBQ Sauce | menu/bbq-sauce.webp | 960×960 | 146 KB | 1254×1254 | معتمدة |
| بيكانتي صوص | Piccante Sauce | menu/piccante-sauce.webp | 960×960 | 174 KB | 1254×1254 | معتمدة |
| ديناميت صوص | Dynamite Sauce | menu/dynamite-sauce.webp | 960×960 | 194 KB | 1254×1254 | معتمدة |
| هوت هني صوص | Hot Honey Sauce | menu/hot-honey-sauce.webp | 960×960 | 123 KB | 1254×1254 | معتمدة |
| كريم ثوم صوص | Garlic Cream Sauce | menu/garlic-cream-sauce.webp | 960×960 | 99 KB | 1254×1254 | معتمدة |
| ماك سموك صوص | Mac Smoke Sauce | — | — | — | 303×267 (شعار) | ناقصة |
| كريمي كاتش صوص | Creamy Ketch Sauce | — | — | — | 303×267 (شعار) | ناقصة |
| كول سلو | Coleslaw | menu/coleslaw.webp | 960×960 | 109 KB | 1254×1254 | معتمدة |
| ذرة بالمايونيز | Corn with Mayo | menu/corn-mayo.webp | 960×960 | 99 KB | 1254×1254 | معتمدة |
| تشيروز كلاسيك | Classic Churros | menu/churros-classic.webp | 960×960 | 307 KB | 1254×1254 | معتمدة |
| تشيروز بالصوصات | Churros with Sauces | menu/churros-sauces.webp | 960×960 | 276 KB | 1254×1254 | معتمدة |
| عصير الموسم | Seasonal Juice | menu/seasonal-juice.webp | 960×960 | 105 KB | 1254×1254 | معتمدة |
| كوكاكولا | Coca-Cola | menu/coca-cola.webp | 640×960 | 23 KB | 853×1280 | معتمدة |
| سبرايت | Sprite | menu/sprite.webp | 640×960 | 28 KB | 853×1280 | معتمدة |
| مياه | Water 500ml | menu/water.webp | 720×960 | 30 KB | 960×1280 | معتمدة |

**الإجمالي:** 81 ملف WebP + أيقونة، 8982 KB.
كل صورة صنف بنسختين: 960px للبطاقة و480px للهاتف.

## الأصول الناقصة

خمسة أصناف مصدرها يعرض الشعار بدل صورة الطعام. لم يُستخدم الشعار كصورة صنف.
راجع `docs/menu-source.md` لقائمتها.

لا توجد صور تقييمات ولا صور تواصل اجتماعي ولا صور عروض بعد.
