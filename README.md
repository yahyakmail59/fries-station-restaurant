# Fries Station — فرايز ستيشن

موقع مطعم **فرايز ستيشن** (Fries Station) — تطبيق Django يضم واجهة عامة ثنائية اللغة
(عربي RTL / إنجليزي LTR)، وسلة طلب تُسعَّر على الخادم، وحجز طاولات، ولوحة تحكم تشغيلية
تشمل الكاشير وسجل العملاء وإدارة المحتوى.

> **حالة المشروع:** خط أساس وظيفي. إعادة الهوية البصرية ومحتوى القائمة قيد التنفيذ
> على فرع `rebrand/fries-station`. راجع `docs/functional-parity.md` عند توفره.

## المتطلبات

- Python 3.11
- الحزم في `requirements.txt` (Django 5.2، Pillow، WhiteNoise، وغيرها)

## التشغيل محليًا (Windows / PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

| الوجهة | الرابط |
|---|---|
| الموقع | http://127.0.0.1:8000/ |
| القائمة الكاملة | http://127.0.0.1:8000/menu/ |
| لوحة التحكم | http://127.0.0.1:8000/dashboard/ |
| الكاشير | http://127.0.0.1:8000/dashboard/cashier/ |
| لوحة Django | http://127.0.0.1:8000/admin/ |

## الفحص والاختبار

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## الإعداد

كل الإعدادات الحساسة تُقرأ من متغيرات البيئة. انسخ `.env.example` وعدّله:

- `DJANGO_SECRET_KEY` — إلزامي عند `DJANGO_DEBUG=0`؛ المشروع يرفض الإقلاع بدونه.
- `DJANGO_ALLOWED_HOSTS` و `DJANGO_CSRF_TRUSTED_ORIGINS` — مطلوبان في الإنتاج.
- `DATABASE_URL` — للانتقال من SQLite إلى PostgreSQL.
- `AWS_STORAGE_BUCKET_NAME` — عند ضبطه تنتقل صور الإدارة إلى S3 تلقائيًا.

لا تُرفع `.env` ولا `db.sqlite3` إلى Git.

## البنية

```text
config/       إعدادات Django والمسارات الجذرية
restaurant/   التطبيق: النماذج، الـviews، اللوحة، الكاشير، الإيصال، الاختبارات
templates/    القوالب
static/       CSS و JavaScript والصور
media/        الصور المرفوعة من لوحة الإدارة (خارج Git)
```

## ملاحظات تقنية

- **أسعار الطلبات تُحسب على الخادم.** المتصفح يرسل معرّف الصنف والكمية فقط؛ أي سعر
  يرسله المتصفح يُتجاهل.
- **صفحة الطلب تُفتح بتوكن عشوائي**، لا برقم الطلب القصير، لأنها تعرض بيانات العميل.
- **إيصال PNG يُرسم على الخادم** بخط IBM Plex Sans Arabic. هذا الخط مطلوب لأن نسخة
  Pillow المستخدمة لا تُشكّل العربية بنفسها، والنص يُشكَّل مسبقًا في Python.
