from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('restaurant', '0003_admin_design_controls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurantsettings',
            name='primary_color',
            field=models.CharField(default='#E30613', max_length=20, validators=[RegexValidator(message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='اللون الأحمر الرئيسي'),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='gold_color',
            field=models.CharField(default='#D4AF37', max_length=20, validators=[RegexValidator(message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='اللون الذهبي'),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='background_color',
            field=models.CharField(default='#050505', max_length=20, validators=[RegexValidator(message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='لون الخلفية'),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='surface_color',
            field=models.CharField(default='#111111', max_length=20, validators=[RegexValidator(message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='لون البطاقات'),
        ),
        migrations.AlterField(
            model_name='restaurantsettings',
            name='whatsapp_color',
            field=models.CharField(default='#25D366', max_length=20, validators=[RegexValidator(message='أدخل لونًا بصيغة سداسية صحيحة مثل #E30613.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='لون واتساب'),
        ),
    ]
