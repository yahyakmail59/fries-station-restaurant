from django.db import migrations, models


NEW_COPY = {
    'hero_title_ar': 'فرايز مقرمشة تُقلى عند الطلب',
    'hero_title_en': 'Fried to order. Your way.',
    'hero_text_ar': 'اختر وجبتك وحجمك، راجع السعر، ثم أرسل طلبك جاهزًا عبر واتساب. متاح للاستلام أو التوصيل.',
    'hero_text_en': 'Choose your meal and size, review the price, then send your ready order on WhatsApp. Pickup and delivery are available.',
    'menu_title_ar': 'اختر قسمك المفضل',
    'menu_title_en': 'Choose a Menu Category',
    'featured_title_ar': 'اختيارات فرايز ستيشن',
    'featured_title_en': 'Fries Station Picks',
    'order_cta_ar': 'ابدأ طلبك',
    'order_cta_en': 'Start your order',
    'menu_cta_ar': 'شاهد المنيو والأسعار',
    'menu_cta_en': 'See menu & prices',
    'whatsapp_panel_text_ar': 'راجع الأصناف والمجموع، ثم أرسل طلبك برسالة واتساب واحدة.',
    'whatsapp_panel_text_en': 'Review your items and total, then send the order in one WhatsApp message.',
}


OLD_COPY = {
    'hero_title_ar': ('من هنا تبدأ… المتعة', 'مقرمشة. ذهبية. مثالية.'),
    'hero_title_en': ('Crispy. Golden. Perfect.',),
    'hero_text_ar': ('بطاطا مقرمشة ودجاج مقلي طازج، مع صوصاتنا الخاصة. سريع، طازج، ولذيذ.',),
    'hero_text_en': ('Crispy fries and freshly fried chicken, with our own sauces. Fast, fresh and delicious.',),
    'menu_title_ar': ('استكشف أقسام القائمة',),
    'menu_title_en': ('Explore Our Menu',),
    'featured_title_ar': ('الأصناف المميزة',),
    'featured_title_en': ('Featured Menu',),
    'order_cta_ar': ('اطلب الآن عبر واتساب',),
    'order_cta_en': ('Order on WhatsApp',),
    'menu_cta_ar': ('استعرض القائمة',),
    'menu_cta_en': ('View Menu',),
    'whatsapp_panel_text_ar': ('خدمة سريعة، رد فوري، وطلب سهل.',),
    'whatsapp_panel_text_en': ('Fast service, quick reply and an easy order.',),
}


def refresh_unchanged_copy(apps, schema_editor):
    settings_model = apps.get_model('restaurant', 'RestaurantSettings')
    for site in settings_model.objects.all():
        changed = []
        for field, old_values in OLD_COPY.items():
            if getattr(site, field) in old_values:
                setattr(site, field, NEW_COPY[field])
                changed.append(field)
        if changed:
            site.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [('restaurant', '0014_tiktok_link')]

    operations = [
        migrations.AlterField(model_name='restaurantsettings', name='hero_title_ar', field=models.CharField(default=NEW_COPY['hero_title_ar'], max_length=180, verbose_name='عنوان الواجهة بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='hero_title_en', field=models.CharField(default=NEW_COPY['hero_title_en'], max_length=180, verbose_name='عنوان الواجهة بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='hero_text_ar', field=models.TextField(default=NEW_COPY['hero_text_ar'], verbose_name='وصف الواجهة بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='hero_text_en', field=models.TextField(default=NEW_COPY['hero_text_en'], verbose_name='وصف الواجهة بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='menu_title_ar', field=models.CharField(default=NEW_COPY['menu_title_ar'], max_length=160, verbose_name='عنوان أقسام القائمة بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='menu_title_en', field=models.CharField(default=NEW_COPY['menu_title_en'], max_length=160, verbose_name='عنوان أقسام القائمة بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='featured_title_ar', field=models.CharField(default=NEW_COPY['featured_title_ar'], max_length=160, verbose_name='عنوان الأطباق المميزة بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='featured_title_en', field=models.CharField(default=NEW_COPY['featured_title_en'], max_length=160, verbose_name='عنوان الأطباق المميزة بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='order_cta_ar', field=models.CharField(default=NEW_COPY['order_cta_ar'], max_length=100, verbose_name='نص زر الطلب بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='order_cta_en', field=models.CharField(default=NEW_COPY['order_cta_en'], max_length=100, verbose_name='نص زر الطلب بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='menu_cta_ar', field=models.CharField(default=NEW_COPY['menu_cta_ar'], max_length=100, verbose_name='نص زر القائمة بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='menu_cta_en', field=models.CharField(default=NEW_COPY['menu_cta_en'], max_length=100, verbose_name='نص زر القائمة بالإنجليزية')),
        migrations.AlterField(model_name='restaurantsettings', name='whatsapp_panel_text_ar', field=models.CharField(default=NEW_COPY['whatsapp_panel_text_ar'], max_length=180, verbose_name='وصف صندوق واتساب بالعربية')),
        migrations.AlterField(model_name='restaurantsettings', name='whatsapp_panel_text_en', field=models.CharField(default=NEW_COPY['whatsapp_panel_text_en'], max_length=180, verbose_name='وصف صندوق واتساب بالإنجليزية')),
        migrations.RunPython(refresh_unchanged_copy, migrations.RunPython.noop),
    ]
