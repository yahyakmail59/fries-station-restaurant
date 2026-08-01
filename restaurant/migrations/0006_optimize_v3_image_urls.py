import re

from django.db import migrations

V3_FULL_IMAGE = re.compile(r'^/static/restaurant/img/v3/(?P<name>[\w-]+)\.webp$')


def _to_960(url):
    match = V3_FULL_IMAGE.match(url or '')
    if not match or match.group('name').endswith('-960'):
        return url
    return f"/static/restaurant/img/v3/{match.group('name')}-960.webp"


def optimize_images(apps, schema_editor):
    MenuItem = apps.get_model('restaurant', 'MenuItem')
    Offer = apps.get_model('restaurant', 'Offer')
    SocialPost = apps.get_model('restaurant', 'SocialPost')

    for model in (MenuItem, Offer):
        for obj in model.objects.exclude(image_url=''):
            optimized = _to_960(obj.image_url)
            if optimized != obj.image_url:
                obj.image_url = optimized
                obj.save(update_fields=['image_url'])

    # These rows are already hidden from the site by the home view filter;
    # removing them keeps the admin free of previews pointing at retired demo files.
    SocialPost.objects.filter(image='', image_url__contains='/demo/').delete()


def restore_images(apps, schema_editor):
    MenuItem = apps.get_model('restaurant', 'MenuItem')
    Offer = apps.get_model('restaurant', 'Offer')
    for model in (MenuItem, Offer):
        for obj in model.objects.filter(image_url__endswith='-960.webp'):
            obj.image_url = obj.image_url.replace('-960.webp', '.webp')
            obj.save(update_fields=['image_url'])


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0005_about_section_fields'),
    ]

    operations = [
        migrations.RunPython(optimize_images, restore_images),
    ]
