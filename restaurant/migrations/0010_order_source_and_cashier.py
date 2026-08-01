from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('restaurant', '0009_order_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='source',
            field=models.CharField(
                choices=[('online', 'أونلاين'), ('cashier', 'داخل المطعم')],
                default='online',
                max_length=20,
                verbose_name='مصدر الطلب',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_count',
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[MinValueValidator(1), MaxValueValidator(100)],
                verbose_name='عدد الزبائن',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='table_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='رقم الطاولة'),
        ),
        migrations.AddField(
            model_name='order',
            name='cashier',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cashier_orders',
                to=settings.AUTH_USER_MODEL,
                verbose_name='الكاشير',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='fulfillment',
            field=models.CharField(
                choices=[
                    ('pickup', 'استلام من المطعم'),
                    ('delivery', 'ديليفري'),
                    ('dine_in', 'داخل المطعم'),
                ],
                default='pickup',
                max_length=20,
                verbose_name='طريقة الاستلام',
            ),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(
                fields=['source', '-created_at'],
                name='restaurant__source_9241eb_idx',
            ),
        ),
    ]
