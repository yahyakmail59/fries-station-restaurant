import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0014_tiktok_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurantsettings',
            name='delivery_enabled',
            field=models.BooleanField(
                default=False,
                help_text='عند إيقافه يختفي خيار التوصيل من السلة ويرفض الخادم طلبات التوصيل.',
                verbose_name='تفعيل التوصيل',
            ),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='reservation_open_time',
            field=models.TimeField(default=datetime.time(11, 30), verbose_name='بداية استقبال الحجوزات'),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='reservation_close_time',
            field=models.TimeField(
                default=datetime.time(23, 30),
                help_text='يمكن أن تكون بعد منتصف الليل إذا تغيّرت ساعات العمل لاحقًا.',
                verbose_name='نهاية استقبال الحجوزات',
            ),
        ),
    ]
