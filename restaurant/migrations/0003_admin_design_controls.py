from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0002_landing_content_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurantsettings',
            name='background_color',
            field=models.CharField(default='#050505', max_length=20, verbose_name='لون الخلفية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='footer_text_ar',
            field=models.CharField(default='رحلة من النكهات العالمية والشرقية الأصلية.', max_length=255, verbose_name='وصف التذييل بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='footer_text_en',
            field=models.CharField(default='A journey of authentic global and oriental flavours.', max_length=255, verbose_name='وصف التذييل بالإنجليزية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='gold_color',
            field=models.CharField(default='#D4AF37', max_length=20, verbose_name='اللون الذهبي'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='menu_cta_ar',
            field=models.CharField(default='استعرض القائمة', max_length=100, verbose_name='نص زر القائمة بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='menu_cta_en',
            field=models.CharField(default='View Menu', max_length=100, verbose_name='نص زر القائمة بالإنجليزية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='og_image',
            field=models.ImageField(blank=True, upload_to='branding/', verbose_name='صورة المشاركة الاجتماعية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='order_cta_ar',
            field=models.CharField(default='اطلب الآن عبر واتساب', max_length=100, verbose_name='نص زر الطلب بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='order_cta_en',
            field=models.CharField(default='Order on WhatsApp', max_length=100, verbose_name='نص زر الطلب بالإنجليزية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='primary_color',
            field=models.CharField(default='#E30613', max_length=20, verbose_name='اللون الأحمر الرئيسي'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='seo_description_ar',
            field=models.TextField(blank=True, verbose_name='وصف SEO بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='seo_description_en',
            field=models.TextField(blank=True, verbose_name='وصف SEO بالإنجليزية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='seo_title_ar',
            field=models.CharField(blank=True, max_length=180, verbose_name='عنوان SEO بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='seo_title_en',
            field=models.CharField(blank=True, max_length=180, verbose_name='عنوان SEO بالإنجليزية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='show_categories',
            field=models.BooleanField(default=True, verbose_name='إظهار أقسام القائمة'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='show_featured',
            field=models.BooleanField(default=True, verbose_name='إظهار الأطباق المميزة'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='surface_color',
            field=models.CharField(default='#111111', max_length=20, verbose_name='لون البطاقات'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='whatsapp_color',
            field=models.CharField(default='#25D366', max_length=20, verbose_name='لون واتساب'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='whatsapp_panel_text_ar',
            field=models.CharField(default='خدمة سريعة، رد فوري، وطلب سهل.', max_length=180, verbose_name='وصف صندوق واتساب بالعربية'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='whatsapp_panel_text_en',
            field=models.CharField(default='Fast service, quick reply and an easy order.', max_length=180, verbose_name='وصف صندوق واتساب بالإنجليزية'),
        ),
    ]
