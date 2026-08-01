import datetime

import restaurant.models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0006_optimize_v3_image_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurantsettings',
            name='hero_image_url',
            field=models.CharField(
                blank=True,
                max_length=500,
                validators=[restaurant.models.image_source_validator],
                verbose_name='رابط أو مسار صورة الواجهة البديل',
            ),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='show_featured',
            field=models.BooleanField(default=True, verbose_name='إظهار قائمة الأطباق'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='reservation_open_time',
            field=models.TimeField(default=datetime.time(8, 0), verbose_name='بداية استقبال الحجوزات'),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='reservation_close_time',
            field=models.TimeField(
                default=datetime.time(2, 0),
                help_text='يمكن أن تكون بعد منتصف الليل، مثل 02:00.',
                verbose_name='نهاية استقبال الحجوزات',
            ),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='reservation_slot_minutes',
            field=models.PositiveSmallIntegerField(
                choices=[(15, '15 دقيقة'), (30, '30 دقيقة'), (60, '60 دقيقة')],
                default=30,
                verbose_name='مدة فترة الحجز',
            ),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='max_reservations_per_slot',
            field=models.PositiveSmallIntegerField(
                default=6,
                validators=[MinValueValidator(1), MaxValueValidator(50)],
                verbose_name='الحد الأقصى للحجوزات في الفترة',
            ),
        ),
        migrations.AddField(
            model_name='restaurantsettings',
            name='max_reservation_days_ahead',
            field=models.PositiveSmallIntegerField(
                default=90,
                validators=[MinValueValidator(1), MaxValueValidator(365)],
                verbose_name='أقصى عدد أيام للحجز المسبق',
            ),
        ),
        *[
            migrations.AlterField(
                model_name=model_name,
                name='image_url',
                field=models.CharField(
                    blank=True,
                    max_length=500,
                    validators=[restaurant.models.image_source_validator],
                    verbose_name='رابط أو مسار صورة بديل',
                ),
            )
            for model_name in ('category', 'menuitem', 'offer', 'socialpost')
        ],
        migrations.AddIndex(
            model_name='reservation',
            index=models.Index(fields=['date', 'time', 'status'], name='restaurant__date_4901a7_idx'),
        ),
    ]
