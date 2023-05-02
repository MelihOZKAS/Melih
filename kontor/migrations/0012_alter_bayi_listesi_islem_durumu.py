# Generated by Django 4.2 on 2023-05-02 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kontor', '0011_bakiyehareketleri_onceki_borc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bayi_listesi',
            name='islem_durumu',
            field=models.CharField(choices=[('islem_sec', 'işlem Türünü Seç'), ('nakit_ekle', 'Nakit/Havele/EFT Bakiye Ekle'), ('borc_ve_bakiye_ekle', 'Hem Borç Hem Bakiye Ekle'), ('bakiye_dus', 'Bakiye Düş'), ('sadece_borc_ekle', 'Sadece Borç Ekle')], default='islem_sec', max_length=20),
        ),
    ]