# Generated by Django 4.2 on 2023-05-02 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kontor', '0007_banka'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bakiyehareketleri',
            options={'verbose_name': 'Bakiye Hareketleri', 'verbose_name_plural': 'Bakiye Hareketleri'},
        ),
        migrations.AlterModelOptions(
            name='banka',
            options={'verbose_name': 'Bankalar', 'verbose_name_plural': 'Bankalar'},
        ),
        migrations.AlterModelOptions(
            name='bayi_listesi',
            options={'verbose_name': 'Bayi Listesi', 'verbose_name_plural': 'Bayi Listesi'},
        ),
    ]