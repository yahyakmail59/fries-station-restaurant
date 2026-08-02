# نشر فرايز ستيشن على PythonAnywhere

PythonAnywhere هو الخيار الأول لهذا المشروع لأن التطبيق Django/WSGI جاهز له،
ويستخدم SQLite بصورة مناسبة لعامل تطبيق واحد في البداية. لا يتم تنفيذ أي خطوة
خارجية من هذا الدليل قبل موافقة المالك.

## 1. القيم المطلوبة قبل البدء

- اسم حساب PythonAnywhere.
- العنوان المبدئي: `https://<username>.pythonanywhere.com`.
- الدومين النهائي إن وُجد لاحقًا.
- قيمة سرية طويلة جديدة لـ`DJANGO_SECRET_KEY`.
- قرار التخزين: `media/` محلي في البداية، أو S3 عند الحاجة.

رقم واتساب المبدئي يبقى `972597862389`، ويمكن تغييره من
`لوحة التحكم ← إعدادات الموقع` من دون نشر كود جديد.

## 2. إنشاء البيئة

من Bash Console في PythonAnywhere:

```bash
git clone https://github.com/yahyakmail59/fries-station-restaurant.git
cd fries-station-restaurant
git switch rebrand/fries-station
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

في Web tab:

- Source code: `/home/<username>/fries-station-restaurant`
- Virtualenv: `/home/<username>/fries-station-restaurant/.venv`
- WSGI: انسخ القيم من `deploy/pythonanywhere_wsgi.py.example` ثم استبدل
  placeholders داخل ملف الخادم فقط.

لا تضع المفتاح السري أو كلمة مرور البريد أو مفاتيح S3 داخل Git.

## 3. قاعدة البيانات والمحتوى

للتثبيت الأول فقط:

```bash
cd /home/<username>/fries-station-restaurant
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_menu
.venv/bin/python manage.py createsuperuser
```

لا تستخدم `seed_menu --force` بعد استقبال طلبات حقيقية.

## 4. الملفات الثابتة والصور

```bash
.venv/bin/python manage.py collectstatic --noinput
```

أضف في Web tab:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/fries-station-restaurant/staticfiles` |
| `/media/` | `/home/<username>/fries-station-restaurant/media` |

عند استخدام S3 لاحقًا لا تضف mapping محليًا لـ`/media/`، واضبط متغيرات AWS
في WSGI على الخادم.

## 5. Staging

اترك في ملف WSGI:

```python
os.environ['DJANGO_SITE_NOINDEX'] = '1'
```

هذا يضيف `X-Robots-Tag: noindex, nofollow` لكل الاستجابات ويجعل `robots.txt`
يرفض فهرسة الموقع كله. بعد تعديل WSGI اضغط Reload في Web tab.

اختبارات Staging المطلوبة:

1. الصفحة الرئيسية والقائمة بالعربية والإنجليزية.
2. الاستلام والتوصيل وإنشاء طلب تجريبي آمن.
3. الحجز، ثم حذف بياناته التجريبية من لوحة الإدارة.
4. لوحة الإدارة والكاشير والصلاحيات.
5. الصور وstatic و404 و500 وسجل الأخطاء.
6. الهاتف 360px وسطح المكتب 1440px.

## 6. النسخ الاحتياطي

أنشئ المجلد مرة واحدة:

```bash
mkdir -p /home/<username>/backups/fries-station
```

قبل كل نشر، استخدم اسمًا زمنيًا واضحًا:

```bash
cd /home/<username>/fries-station-restaurant
sqlite3 db.sqlite3 ".backup '/home/<username>/backups/fries-station/db-before-deploy.sqlite3'"
tar -czf /home/<username>/backups/fries-station/media-before-deploy.tar.gz media
git rev-parse HEAD > /home/<username>/backups/fries-station/commit-before-deploy.txt
```

لا تضع النسخ الاحتياطية داخل مستودع Git. نزّل نسخة خارج الحساب دوريًا.

## 7. نشر تحديث

```bash
cd /home/<username>/fries-station-restaurant
git status --short
git pull --ff-only origin rebrand/fries-station
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
```

بعد نجاح الأوامر اضغط Reload ثم راجع Error log وServer log.

## 8. الانتقال إلى الإنتاج

بعد الموافقة الصريحة فقط:

- اربط الدومين واضبط `DJANGO_ALLOWED_HOSTS` و`DJANGO_CSRF_TRUSTED_ORIGINS`.
- اجعل `DJANGO_SITE_NOINDEX=0`.
- فعّل `DJANGO_SECURE_SSL_REDIRECT=1` بعد عمل HTTPS.
- ابدأ HSTS بقيمة صغيرة، ثم ارفعها تدريجيًا بعد التأكد من HTTPS.
- أعد Reload وافحص الطلب والحجز والكاشير والصور.

سيعرض `manage.py check --deploy` التحذيرين W005 وW021 ما دامت حماية HSTS
للـsubdomains وpreload متوقفة. لا تفعّلهما قبل التأكد أن الدومين وكل subdomains
تعمل حصريًا عبر HTTPS. عند تحقق ذلك اضبط:

```text
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=1
DJANGO_SECURE_HSTS_PRELOAD=1
```

تم اختبار الإعدادات محليًا بهذه القيم، ونجح `check --deploy` بلا تحذيرات.

## 9. الرجوع الآمن

إذا ظهر خطأ حرج:

1. لا تنفّذ migrations إضافية ولا تغيّر البيانات يدويًا.
2. اقرأ hash السابق من `commit-before-deploy.txt`.
3. استخدم `git switch --detach <known-good-hash>` من دون إعادة كتابة التاريخ.
4. استعد قاعدة SQLite عبر ملف النسخة الاحتياطية بعد إيقاف استقبال الطلبات.
5. استعد `media/` من ملف tar عند الحاجة.
6. شغّل `collectstatic` واضغط Reload.
7. افحص الصفحة والطلب والحجز والسجلات قبل إعادة فتح الخدمة.

إذا كانت migration الجديدة غير قابلة للعكس، استعادة نسخة قاعدة البيانات هي مسار
الرجوع، وليس تنفيذ تجارب مباشرة على الإنتاج.
