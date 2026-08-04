from django.db import migrations


EXTRAS_IMAGE_URL = '/static/restaurant/img/fries-station/categories/extras.webp'


def set_extras_image(apps, schema_editor):
    """Give the extras section its own cover.

    It was the one section without a photograph of its own, borrowing the
    sauces cover, and the replacement arrived as an admin upload. An upload
    lives in media/, which is outside the repository and therefore never
    reaches the server, so the cover is shipped as a static file like the
    other eight and pointed at through image_url.

    Category.image_src prefers the uploaded image over image_url, so any
    upload still sitting on this row has to be cleared or it would keep
    winning over the static file.
    """
    category = apps.get_model('restaurant', 'Category')
    category.objects.filter(slug='extras').update(image='', image_url=EXTRAS_IMAGE_URL)


class Migration(migrations.Migration):
    dependencies = [
        ('restaurant', '0016_missing_item_images'),
    ]

    operations = [
        migrations.RunPython(set_extras_image, migrations.RunPython.noop),
    ]
