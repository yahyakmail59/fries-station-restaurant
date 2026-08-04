from django.db import migrations


IMAGE_URLS = {
    'Boom Fries': '/static/restaurant/img/fries-station/menu/boom-fries.webp',
    'Piccata Fries': '/static/restaurant/img/fries-station/menu/piccata-fries.webp',
    'Jumbo Fries': '/static/restaurant/img/fries-station/menu/shrimp-cut-fries.webp',
    'Mac Smoke Sauce': '/static/restaurant/img/fries-station/menu/mac-smoke-sauce.webp',
    'Creamy Ketch Sauce': '/static/restaurant/img/fries-station/menu/creamy-ketch-sauce.webp',
    'Vienna Bread': '/static/restaurant/img/fries-station/menu/vienna-bread.webp',
}


def add_missing_item_images(apps, schema_editor):
    menu_item = apps.get_model('restaurant', 'MenuItem')
    for name_en, image_url in IMAGE_URLS.items():
        menu_item.objects.filter(name_en=name_en, image_url='').update(image_url=image_url)


class Migration(migrations.Migration):
    dependencies = [
        ('restaurant', '0015_conversion_first_copy'),
    ]

    operations = [
        migrations.RunPython(add_missing_item_images, migrations.RunPython.noop),
    ]
