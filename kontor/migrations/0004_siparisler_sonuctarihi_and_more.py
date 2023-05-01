# Generated by Django 4.2 on 2023-05-01 18:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kontor', '0003_kontorlist_alternatifyapilmasin'),
    ]

    operations = [
        migrations.AddField(
            model_name='siparisler',
            name='SonucTarihi',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='kontorlist',
            name='AlternatifYapilmasin',
            field=models.BooleanField(default=False, verbose_name='Alternatif Yapmıyorum'),
        ),
        migrations.AlterField(
            model_name='siparisler',
            name='OlusturmaTarihi',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
