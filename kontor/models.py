from django.db import models
from django.contrib.auth.models import User


# Create your models here.



class AnaOperator(models.Model):
    AnaOperatorler = models.CharField(max_length=100,default="AnaOperator")


    class Meta:
        verbose_name = "AnaOperator"
        verbose_name_plural = "AnaOperator"

    def save(self,*args,**kargs):
        super().save(args,kargs)
    def __str__(self):
        return f"{self.AnaOperatorler}"
class AltOperator(models.Model):

    AltOperatorler    = models.CharField(max_length=100,default="AltOperatorler")
    class Meta:
        verbose_name = "AltOperatorler"
        verbose_name_plural = "AltOperatorler"

    def save(self,*args,**kargs):
        super().save(args,kargs)
    def __str__(self):
        return f"{self.AltOperatorler}"


class Durumlar(models.Model):
    askida = 1
    ISLEMDE = 100
    IPTAL_EDILDI = 97
    ALTERNATIF_DENEYEN = 10
    AnaPaketGoner = 98
    Sorguda = 44
    AltKontrol = 31
    Basarili = 99
    Alternatif_Gonderimbekler = 70
    Alternatif_Gonderim_Bekliyor = 73
    Alternatif_islemde = 71
    Alternatif_Cevap_Bekliyor = 72
    Alternatif_Direk_Gonder = 80
    SorguCevap = 101
    SorguTamam = 102
    AnaPaketSonucBekler = 998



    DURUM_CHOICES = (
        (askida, 'Askida'),#1
        (ISLEMDE, 'İşlemde'),#100
        (IPTAL_EDILDI, 'İptal ET'),#97
        (ALTERNATIF_DENEYEN, 'Alternatif Paketler Deneniyor'),#10
        (AnaPaketGoner, 'Direk Ana Paketi Gönder'),#98
        (AnaPaketSonucBekler, 'AnaPaketSonucBekler'),#98
        (Sorguda, 'Sorguda'),#44
        (SorguCevap, 'SorguCevap'),#101
        (SorguTamam, 'SorguTamam'),#102
        (AltKontrol, 'Alternafi Kontrol'),#31
        (Basarili, 'Basarili'),#99
        (Alternatif_Gonderimbekler, 'Alternatif Gönderim Gönder'),#70
        (Alternatif_Gonderim_Bekliyor, 'Alternatif Gönderim Bekliyor'),#70
        (Alternatif_islemde, 'Alternatif islemde'),#71
        (Alternatif_Cevap_Bekliyor, 'Alternatif Cevap Bekliyor'),#72
        (Alternatif_Direk_Gonder, 'Alternatif Direk Gönder'),#80
    )

    durum_id = models.PositiveSmallIntegerField(choices=DURUM_CHOICES, unique=True)

    def __str__(self):
        return self.get_durum_id_display()


class Kategori(models.Model):
    KategoriAdi = models.CharField(max_length=100,default="ApiAdi")
    Operatoru = models.ForeignKey(AnaOperator, on_delete=models.CASCADE, null=True)
    KategoriAltOperatoru = models.ForeignKey(AltOperator, on_delete=models.CASCADE, null=True)
    GorunecekName = models.CharField(max_length=100,default="GorulecekISIM")
    GorunecekSira = models.DecimalField(max_digits=100, decimal_places=0,default= 0)
    Aktifmi = models.BooleanField(default=True)
    #MinMax = models.DecimalField(max_digits=100, decimal_places=0, default=0)
    class Meta:
        verbose_name = "Operatör Listesi"
        verbose_name_plural = "Operatör Listesi"


    def save(self,*args,**kargs):
        super().save(args,kargs)

    def __str__(self):
        return f"{self.KategoriAdi}"

class ApiKategori(models.Model):
    ApiYazilimAdi = models.CharField(max_length=100,default="ApiAdi")
    class Meta:
        verbose_name = "Api Kategorisi"
        verbose_name_plural = "Api Kategorisi"

    def save(self,*args,**kargs):
        super().save(args,kargs)
    def __str__(self):
        return f"{self.ApiYazilimAdi}"









class Apiler(models.Model):
    ApiTuru = models.ForeignKey(ApiKategori, on_delete=models.CASCADE, null=True)
    Apiadi = models.CharField(max_length=100,default="ApiAdiGiriniz")
    ApiBakiye = models.DecimalField(max_digits=100, decimal_places=2,default="0,00")
    ApiTanim = models.CharField("Api Tanim",max_length=100, default="",null=True,blank=True)
    HataManuel = models.BooleanField("Hataya Düşeni Manuelde Beklet", default=False)
    ApiAktifmi = models.BooleanField("Aktif mi ?", default=True)
    SiteAdresi = models.CharField("Site Adresi",max_length=100, default="")
    Kullanicikodu = models.CharField("Kullanıcı Kodu",max_length=100, default="")
    Kullaniciadi = models.CharField("Kullanıcı Adi",max_length=100,default="")
    Sifre = models.CharField("Şifre",max_length=100,default="")
    RefNumarasi = models.PositiveIntegerField(default=1)


    class Meta:
        verbose_name = "Api Listesi"
        verbose_name_plural = "Api Listesi"

    def save(self, *args, **kargs):
        super().save(args, kargs)

    def __str__(self):
        return f"{self.Apiadi} - {self.ApiBakiye}"







class KontorList(models.Model):
    Urun_adi = models.CharField(max_length=100)
    Urun_Detay = models.CharField(max_length=100)
    Kupur = models.DecimalField(max_digits=100, decimal_places=2)
    zNetKupur = models.DecimalField(max_digits=100, decimal_places=2, null=True,blank=True)
    GunSayisi = models.DecimalField(max_digits=31, decimal_places=2, default=0)
    MaliyetFiyat = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    SatisFiyat = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    alternatif_urunler = models.ManyToManyField("self", through='Alternatif', symmetrical=False,
                                                related_name='alternatif_of', blank=True)


    HeryoneDK = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    Sebekeici = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    internet = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    SMS = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    YurtDisiDk = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    Aktifmi = models.BooleanField("Aktif mi ?", default=True)
    AlternatifYapilmasin = models.BooleanField("Alternatif Yapmıyorum", default=False)
    Kategorisi = models.ForeignKey(Kategori, on_delete=models.CASCADE, null=True)
    api1 = models.ForeignKey(Apiler, on_delete=models.CASCADE, null=True,blank=True)
    api2 = models.ForeignKey(Apiler, on_delete=models.CASCADE,related_name='api2', null=True,blank=True)
    api3 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='api3', null=True,blank=True)

    #def alternatif_urunler(self):
    #    AlternativeProduct.objects.filter(main_product=self).delete()
    #    alternatif_urunler = []
    #    for urun in KontorList.objects.exclude(id=self.id):
    #        if urun.Aktifmi == True:
    #            if urun.MaliyetFiyat <= self.MaliyetFiyat and urun.HeryoneDK >= self.HeryoneDK and urun.Kategorisi == self.Kategorisi:
    #                AlternativeProduct.objects.create(
    #                    main_product=self,
    #                    product_id=urun.Kupur,
    #                    product_name=urun.Urun_adi,
    #                    cost_price=urun.MaliyetFiyat
    #                )
    #                alternatif_urunler.append(urun)
#
#
    #    return alternatif_urunler




    class Meta:
        verbose_name = "Kontör Listesi"
        verbose_name_plural = "Kontör Listesi"

    def save(self, *args, **kargs):
        super().save(args, kargs)

    def __str__(self):
        return f"- {self.Kupur} -{self.Urun_adi} - {self.MaliyetFiyat}"

class ApidenCekilenPaketler(models.Model):
    apiler = models.ForeignKey(Apiler, on_delete=models.CASCADE)
    urun_adi = models.CharField(max_length=100, null=True, blank=True)
    kupur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ApiGelen_fiyati = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ApiGelen_operator_adi = models.CharField(max_length=50, null=True, blank=True)
    ApiGelen_operator_tipi = models.CharField(max_length=10, null=True, blank=True)



class Turkcell(models.Model):
    apiler = models.ForeignKey(Apiler, on_delete=models.CASCADE)
    urun_adi = models.CharField(max_length=100,null=True, blank=True)
    kupur = models.DecimalField(max_digits=100, decimal_places=2,null=True, blank=True)
    alis_fiyati = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    eslestirme_operator_adi = models.CharField(max_length=100, null=True, blank=True)
    eslestirme_operator_tipi = models.CharField(max_length=100, null=True, blank=True)
    eslestirme_kupur = models.DecimalField(max_digits=100, decimal_places=2,null=True, blank=True)
    Apiden_gelenler = models.ForeignKey(ApidenCekilenPaketler, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'TurkcellTam'

    def __str__(self):
        return self.urun_adi
class VodafonePaketler(models.Model):
    apiler = models.ForeignKey(Apiler, on_delete=models.CASCADE)
    urun_adi = models.CharField(max_length=100,null=True, blank=True)
    kupur = models.DecimalField(max_digits=100, decimal_places=2,null=True, blank=True)
    alis_fiyati = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    eslestirme_operator_adi = models.CharField(max_length=100, null=True, blank=True)
    eslestirme_operator_tipi = models.CharField(max_length=100, null=True, blank=True)
    eslestirme_kupur = models.DecimalField(max_digits=100, decimal_places=2,null=True, blank=True)
    Apiden_gelenler = models.ForeignKey(ApidenCekilenPaketler, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'VodafonePaketler'
    def __str__(self):
        return self.urun_adi





class Siparisler(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    GelenReferans = models.PositiveIntegerField(unique=True)
    Numara = models.BigIntegerField()
    PaketAdi = models.CharField(max_length=200, null=True, blank=True)
    Operator = models.ForeignKey(AnaOperator, on_delete=models.CASCADE, null=True)
    OperatorTip = models.ForeignKey(AltOperator, on_delete=models.CASCADE, null=True)
    PaketKupur = models.PositiveIntegerField()
    Durum = models.ForeignKey(Durumlar, on_delete=models.PROTECT)
    AnaPaketVar = models.BooleanField("AnaPaketVar", default=False)
    Aciklama = models.TextField(null=True,blank=True)
    BayiAciklama = models.CharField(max_length=200, null=True,blank=True)
    SanalRef = models.PositiveIntegerField(null=True,blank=True)
    Gonderim_Sirasi= models.PositiveIntegerField(null=True,blank=True)
    SanalKategori = models.CharField(max_length=100, blank=True)
    SanalTutar = models.DecimalField("Maliyet",max_digits=100, decimal_places=2, null=True,blank=True)
    SorguPaketID = models.CharField(max_length=1000, blank=True)
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)
    SonucTarihi = models.DateTimeField(null=True, blank=True)
    api1 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Api_1',null=True, blank=True)
    api2 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Api_2', null=True, blank=True)
    api3 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Api_3', null=True, blank=True)
    ManuelApi = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='ManuelApi', null=True, blank=True)

    class Meta:
        verbose_name = "Sipariş Listesi"
        verbose_name_plural = "Sipariş Listesi"

    def __str__(self):
        return f"{self.Numara}- {self.PaketKupur} - {self.Durum}"



class Alternatif(models.Model):
    from_item = models.ForeignKey(KontorList, on_delete=models.CASCADE, related_name='from_alternatifs')
    to_item = models.ForeignKey(KontorList, on_delete=models.CASCADE, related_name='to_alternatifs')

class AlternativeProduct(models.Model):
    main_product = models.ForeignKey(KontorList, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)



class YuklenecekSiparisler(models.Model):
    YuklenecekPaketAdi = models.CharField(max_length=255)
    YuklenecekPaketID = models.IntegerField()
    YuklenecekPaketDurumu = models.ForeignKey(Durumlar, on_delete=models.PROTECT)
    YuklenecekPaketFiyat = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    SanalRefIdesi = models.IntegerField(null=True, blank=True)
    Yukelenecek_Numara = models.ForeignKey(Siparisler, on_delete=models.CASCADE, related_name='yuklenecek_siparisler',null=True, blank=True)
    Gonderim_Sirasi = models.PositiveIntegerField(null=True, blank=True)
    orjinalPaketID = models.PositiveIntegerField(null=True, blank=True)
    Yuklenecek_api1 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Yuklenecek_Api_1', null=True, blank=True)
    Yuklenecek_api2 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Yuklenecek_Api_2', null=True, blank=True)
    Yuklenecek_api3 = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Yuklenecek_Api_3', null=True, blank=True)
    Yukelenecek_Manuel_Api = models.ForeignKey(Apiler, on_delete=models.CASCADE, related_name='Manuel_Api', null=True, blank=True)
    ANAURUNID = models.PositiveIntegerField(null=True,blank=True)

    def __str__(self):
        return self.YuklenecekPaketAdi


#class Bayi_Listesi(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    Bayi_Bakiyesi = models.DecimalField(max_digits=10, decimal_places=2)
#    class Meta:
#        verbose_name = "Bayi Listesi"
#        verbose_name_plural = "Bayi Listesi"



class Banka(models.Model):
    banka_adi = models.CharField(max_length=100)
    hesap_sahibi = models.CharField(max_length=100)
    hesap_numarasi = models.CharField(max_length=100)
    sube_kodu = models.CharField(max_length=100)
    iban = models.CharField(max_length=50)
    aciklama = models.TextField(blank=True)
    bakiye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    BayiGormesin = models.BooleanField("Bayi Gormesin", default=False)
    Aktifmi = models.BooleanField("Aktif mi ?", default=True)

    def __str__(self):
        return self.banka_adi

    class Meta:
        verbose_name = "Bankalar"
        verbose_name_plural = "Bankalar"




class Bayi_Listesi(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Bayi_Bakiyesi = models.DecimalField(max_digits=10, decimal_places=2)
    Tutar = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    secili_banka = models.ForeignKey(Banka, on_delete=models.CASCADE,null=True,default=None)

    def save(self, *args, **kwargs):
        if self.pk is None:  # Yeni bir nesne oluşturuluyorsa
            self.Tutar = 0  # Tutar alanını sıfırla

        # Önce bayi bakiyesine tutarı ekle
        onceki_bakiye = self.Bayi_Bakiyesi
        self.Bayi_Bakiyesi += self.Tutar
        sonraki_bakiye = self.Bayi_Bakiyesi

        # Sonra seçili bankanın bakiyesine de tutarı ekle
        if self.secili_banka is not None and self.Tutar > 0:
            self.secili_banka.bakiye += self.Tutar
            self.secili_banka.save()

        bakiye_hareketi = BakiyeHareketleri.objects.create(
            user=self.user,
            islem_tutari=self.Tutar,
            onceki_bakiye=onceki_bakiye,
            sonraki_bakiye=sonraki_bakiye,
            tarih=timezone.now(),
            aciklama='BankaBakiyesi Eklendi',
            bayi=self,
        )
        bakiye_hareketi.save()

        # En son Bayi_Listesi nesnesini kaydet
        super(Bayi_Listesi, self).save(*args, **kwargs)


        # Tutar alanını sıfırla
        self.Tutar = 0
        super(Bayi_Listesi, self).save(update_fields=['Tutar'])

    class Meta:
        verbose_name = "Bayi Listesi"
        verbose_name_plural = "Bayi Listesi"

class BakiyeHareketleri(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    islem_tutari = models.DecimalField(max_digits=10, decimal_places=2)
    onceki_bakiye = models.DecimalField(max_digits=10, decimal_places=2)
    sonraki_bakiye = models.DecimalField(max_digits=10, decimal_places=2)
    tarih = models.DateTimeField(auto_now_add=True)
    aciklama = models.CharField(max_length=255)
    class Meta:
        verbose_name = "Bakiye Hareketleri"
        verbose_name_plural = "Bakiye Hareketleri"




