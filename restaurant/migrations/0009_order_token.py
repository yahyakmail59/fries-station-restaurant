"""Give every order a high-entropy URL token.

The public order page shows a customer's name, phone and address, and the
short code is only four characters so it can be read over the phone. That
makes it guessable, so the URL keys on this token instead and the code is
kept for humans.

Three steps because the column is unique: add it blank, fill it with
distinct values, then apply the constraint.
"""
import secrets

from django.db import migrations, models


def fill_tokens(apps, schema_editor):
    Order = apps.get_model('restaurant', 'Order')
    for order in Order.objects.filter(token='').only('pk'):
        Order.objects.filter(pk=order.pk).update(token=secrets.token_urlsafe(12))


def clear_tokens(apps, schema_editor):
    apps.get_model('restaurant', 'Order').objects.update(token='')


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_order_orderline'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='token',
            field=models.CharField(default='', editable=False, max_length=32, verbose_name='مفتاح الرابط'),
            preserve_default=False,
        ),
        migrations.RunPython(fill_tokens, clear_tokens),
        migrations.AlterField(
            model_name='order',
            name='token',
            field=models.CharField(editable=False, max_length=32, unique=True, verbose_name='مفتاح الرابط'),
        ),
    ]
