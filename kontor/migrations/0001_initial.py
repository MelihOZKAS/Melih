# Generated by Django 4.2 on 2023-04-24 11:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternatif',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AltOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AltOperatorler', models.CharField(default='AltOperatorler', max_length=100)),
            ],
            options={
                'verbose_name': 'AltOperatorler',
                'verbose_name_plural': 'AltOperatorler',
            },
        ),
        migrations.CreateModel(
            name='AnaOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AnaOperatorler', models.CharField(default='AnaOperator', max_length=100)),
            ],
            options={
                'verbose_name': 'AnaOperator',
                'verbose_name_plural': 'AnaOperator',
            },
        ),
        migrations.CreateModel(
            name='ApidenCekilenPaketler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urun_adi', models.CharField(blank=True, max_length=100, null=True)),
                ('kupur', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ApiGelen_fiyati', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ApiGelen_operator_adi', models.CharField(blank=True, max_length=50, null=True)),
                ('ApiGelen_operator_tipi', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApiKategori',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ApiYazilimAdi', models.CharField(default='ApiAdi', max_length=100)),
            ],
            options={
                'verbose_name': 'Api Kategorisi',
                'verbose_name_plural': 'Api Kategorisi',
            },
        ),
        migrations.CreateModel(
            name='Apiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Apiadi', models.CharField(default='ApiAdiGiriniz', max_length=100)),
                ('ApiBakiye', models.DecimalField(decimal_places=2, default='0,00', max_digits=100)),
                ('ApiTanim', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Api Tanim')),
                ('HataManuel', models.BooleanField(default=False, verbose_name='Hataya Düşeni Manuelde Beklet')),
                ('ApiAktifmi', models.BooleanField(default=True, verbose_name='Aktif mi ?')),
                ('SiteAdresi', models.CharField(default='', max_length=100, verbose_name='Site Adresi')),
                ('Kullanicikodu', models.CharField(default='', max_length=100, verbose_name='Kullanıcı Kodu')),
                ('Kullaniciadi', models.CharField(default='', max_length=100, verbose_name='Kullanıcı Adi')),
                ('Sifre', models.CharField(default='', max_length=100, verbose_name='Şifre')),
                ('RefNumarasi', models.PositiveIntegerField(default=1)),
                ('ApiTuru', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.apikategori')),
            ],
            options={
                'verbose_name': 'Api Listesi',
                'verbose_name_plural': 'Api Listesi',
            },
        ),
        migrations.CreateModel(
            name='Durumlar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('durum_id', models.PositiveSmallIntegerField(choices=[(1, 'Askida'), (100, 'İşlemde'), (97, 'İptal ET'), (10, 'Alternatif Paketler Deneniyor'), (98, 'Direk Ana Paketi Gönder'), (998, 'AnaPaketSonucBekler'), (44, 'Sorguda'), (101, 'SorguCevap'), (102, 'SorguTamam'), (31, 'Alternafi Kontrol'), (99, 'Basarili'), (70, 'Alternatif Gönderim Gönder'), (73, 'Alternatif Gönderim Bekliyor'), (71, 'Alternatif islemde'), (72, 'Alternatif Cevap Bekliyor'), (80, 'Alternatif Direk Gönder'), (80, 'Alternatif Direk Gönder')], unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Kategori',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('KategoriAdi', models.CharField(default='ApiAdi', max_length=100)),
                ('GorunecekName', models.CharField(default='GorulecekISIM', max_length=100)),
                ('GorunecekSira', models.DecimalField(decimal_places=0, default=0, max_digits=100)),
                ('Aktifmi', models.BooleanField(default=True)),
                ('KategoriAltOperatoru', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.altoperator')),
                ('Operatoru', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.anaoperator')),
            ],
            options={
                'verbose_name': 'Operatör Listesi',
                'verbose_name_plural': 'Operatör Listesi',
            },
        ),
        migrations.CreateModel(
            name='Siparisler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('GelenReferans', models.PositiveIntegerField(unique=True)),
                ('Numara', models.BigIntegerField()),
                ('PaketAdi', models.CharField(blank=True, max_length=200, null=True)),
                ('PaketKupur', models.PositiveIntegerField()),
                ('AnaPaketVar', models.BooleanField(default=False, verbose_name='AnaPaketVar')),
                ('Aciklama', models.TextField(blank=True, null=True)),
                ('BayiAciklama', models.CharField(blank=True, max_length=200, null=True)),
                ('SanalRef', models.PositiveIntegerField(blank=True, null=True)),
                ('Gonderim_Sirasi', models.PositiveIntegerField(blank=True, null=True)),
                ('SanalKategori', models.CharField(blank=True, max_length=100)),
                ('SanalTutar', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True, verbose_name='Maliyet')),
                ('SorguPaketID', models.CharField(blank=True, max_length=1000)),
                ('OlusturmaTarihi', models.DateTimeField(auto_now_add=True)),
                ('Durum', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kontor.durumlar')),
                ('ManuelApi', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ManuelApi', to='kontor.apiler')),
                ('Operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.anaoperator')),
                ('OperatorTip', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.altoperator')),
                ('api1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Api_1', to='kontor.apiler')),
                ('api2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Api_2', to='kontor.apiler')),
                ('api3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Api_3', to='kontor.apiler')),
            ],
            options={
                'verbose_name': 'Sipariş Listesi',
                'verbose_name_plural': 'Sipariş Listesi',
            },
        ),
        migrations.CreateModel(
            name='YuklenecekSiparisler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('YuklenecekPaketAdi', models.CharField(max_length=255)),
                ('YuklenecekPaketID', models.IntegerField()),
                ('YuklenecekPaketFiyat', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('SanalRefIdesi', models.IntegerField(blank=True, null=True)),
                ('Gonderim_Sirasi', models.PositiveIntegerField(blank=True, null=True)),
                ('orjinalPaketID', models.PositiveIntegerField(blank=True, null=True)),
                ('ANAURUNID', models.PositiveIntegerField(blank=True, null=True)),
                ('Yukelenecek_Manuel_Api', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Manuel_Api', to='kontor.apiler')),
                ('Yukelenecek_Numara', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='yuklenecek_siparisler', to='kontor.siparisler')),
                ('YuklenecekPaketDurumu', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kontor.durumlar')),
                ('Yuklenecek_api1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Yuklenecek_Api_1', to='kontor.apiler')),
                ('Yuklenecek_api2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Yuklenecek_Api_2', to='kontor.apiler')),
                ('Yuklenecek_api3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Yuklenecek_Api_3', to='kontor.apiler')),
            ],
        ),
        migrations.CreateModel(
            name='VodafonePaketler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urun_adi', models.CharField(blank=True, max_length=100, null=True)),
                ('kupur', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('alis_fiyati', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('eslestirme_operator_adi', models.CharField(blank=True, max_length=100, null=True)),
                ('eslestirme_operator_tipi', models.CharField(blank=True, max_length=100, null=True)),
                ('eslestirme_kupur', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('Apiden_gelenler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.apidencekilenpaketler')),
                ('apiler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kontor.apiler')),
            ],
            options={
                'verbose_name_plural': 'VodafonePaketler',
            },
        ),
        migrations.CreateModel(
            name='Turkcell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urun_adi', models.CharField(blank=True, max_length=100, null=True)),
                ('kupur', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('alis_fiyati', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('eslestirme_operator_adi', models.CharField(blank=True, max_length=100, null=True)),
                ('eslestirme_operator_tipi', models.CharField(blank=True, max_length=100, null=True)),
                ('eslestirme_kupur', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('Apiden_gelenler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.apidencekilenpaketler')),
                ('apiler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kontor.apiler')),
            ],
            options={
                'verbose_name_plural': 'TurkcellTam',
            },
        ),
        migrations.CreateModel(
            name='KontorList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Urun_adi', models.CharField(max_length=100)),
                ('Urun_Detay', models.CharField(max_length=100)),
                ('Kupur', models.DecimalField(decimal_places=2, max_digits=100)),
                ('zNetKupur', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('GunSayisi', models.DecimalField(decimal_places=2, default=0, max_digits=31)),
                ('MaliyetFiyat', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('SatisFiyat', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('HeryoneDK', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('Sebekeici', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('internet', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('SMS', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('YurtDisiDk', models.DecimalField(decimal_places=2, default=0, max_digits=100)),
                ('Aktifmi', models.BooleanField(default=True, verbose_name='Aktif mi ?')),
                ('Kategorisi', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.kategori')),
                ('alternatif_urunler', models.ManyToManyField(blank=True, related_name='alternatif_of', through='kontor.Alternatif', to='kontor.kontorlist')),
                ('api1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kontor.apiler')),
                ('api2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='api2', to='kontor.apiler')),
                ('api3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='api3', to='kontor.apiler')),
            ],
            options={
                'verbose_name': 'Kontör Listesi',
                'verbose_name_plural': 'Kontör Listesi',
            },
        ),
        migrations.CreateModel(
            name='Bayi_Listesi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Bayi_Bakiyesi', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BakiyeHareketleri',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('islem_tutari', models.DecimalField(decimal_places=2, max_digits=10)),
                ('onceki_bakiye', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sonraki_bakiye', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tarih', models.DateTimeField(auto_now_add=True)),
                ('aciklama', models.CharField(max_length=254)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='apidencekilenpaketler',
            name='apiler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kontor.apiler'),
        ),
        migrations.CreateModel(
            name='AlternativeProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('product_name', models.CharField(max_length=255)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('main_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kontor.kontorlist')),
            ],
        ),
        migrations.AddField(
            model_name='alternatif',
            name='from_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_alternatifs', to='kontor.kontorlist'),
        ),
        migrations.AddField(
            model_name='alternatif',
            name='to_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_alternatifs', to='kontor.kontorlist'),
        ),
    ]
