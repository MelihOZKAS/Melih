from django.contrib import admin
from .models import KontorList,Kategori,Apiler,ApiKategori,AlternativeProduct,Siparisler,AnaOperator,AltOperator,YuklenecekSiparisler,Durumlar,Turkcell,ApidenCekilenPaketler,VodafonePaketler,Bayi_Listesi,BakiyeHareketleri
from django.utils.html import format_html
from django.urls import reverse,path
from django.utils import timesince,timezone
from django.http import HttpResponseRedirect

from django.forms import Select, RadioSelect, PasswordInput
from django import forms
import inspect
from django.contrib.auth.models import User


# Register your models here.
class DurumlarAdmin(admin.ModelAdmin):
    list_display = ['durum_id', 'get_durum_id_display']

class AlternativeProductInline(admin.TabularInline):
    model = AlternativeProduct
    extra = 1
    verbose_name_plural = "Alternatif ürünler"





class AdminKontorListesi(admin.ModelAdmin):
    list_display = ("id","Kupur","Urun_adi","MaliyetFiyat","SatisFiyat","Aktifmi","api1","api2","api3", "alternatif_urunler_count",)#"alternatif_urunler",
    list_editable = ("Urun_adi","Aktifmi","MaliyetFiyat","SatisFiyat","api1","api2","api3",)
    search_fields = ("Urun_adi","Kupur",)
    list_filter = ("Kategorisi",)
    inlines = [AlternativeProductInline]

    actions = ['otoyap_action']



    def otoyap_action(self, request, queryset):

        selected = queryset
        for obj in selected:
            alternatif_urunler = []
            AlternativeProduct.objects.filter(main_product=obj).delete()
            for urun in KontorList.objects.exclude(id=obj.id).order_by('MaliyetFiyat'):
                if urun.Aktifmi == True:
                    if urun.MaliyetFiyat < obj.MaliyetFiyat and urun.HeryoneDK >= obj.HeryoneDK and urun.internet >= obj.internet and urun.GunSayisi >= obj.GunSayisi and urun.Kategorisi == obj.Kategorisi:
                        AlternativeProduct.objects.create(
                            main_product=obj,
                            product_id=urun.Kupur,
                            product_name=urun.Urun_adi,
                            cost_price=urun.MaliyetFiyat
                        )
                        alternatif_urunler.append(urun)

        self.message_user(request, "Seçilen Tüm Ürünlerin Alternatif işlemleri  başarıyla tamamlandı.")

    otoyap_action.short_description = "AlternatifleriniYap"

    def alternatif_urunler_count(self, obj):
        return obj.alternativeproduct_set.count()

    alternatif_urunler_count.short_description = "Alternatif Ürünler"

class YuklenecekSiparislerInline(admin.TabularInline):
    model = YuklenecekSiparisler
    extra = 0
    fields = ('YuklenecekPaketAdi', 'ANAURUNID','YuklenecekPaketID', 'YuklenecekPaketDurumu','Gonderim_Sirasi','orjinalPaketID','SanalRefIdesi', 'Yuklenecek_api1', 'Yuklenecek_api2', 'Yuklenecek_api3','Yukelenecek_Manuel_Api',)
    verbose_name = 'Yüklenecek Sipariş'
    verbose_name_plural = 'Yüklenecek Siparişler'
    list_filter = ['Yuklenecek_Api_1', 'Yuklenecek_Api_2']


class DirekGonderInline(admin.TabularInline):
    model = YuklenecekSiparisler
    extra = 0
    fields = ('YuklenecekPaketAdi', 'YuklenecekPaketID', 'YuklenecekPaketDurumu', 'Yukelenecek_Manuel_Api')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "YuklenecekPaketAdi":
            # YuklenecekSiparisler modelindeki YuklenecekPaketAdi özelliklerinin listesi
            choices = [(paket.id, paket.YuklenecekPaketAdi) for paket in YuklenecekSiparisler.objects.all()]

            # Combobox'ın seçeneklerini yukarıda oluşturduğumuz listeye göre ayarla
            kwargs["choices"] = choices

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    verbose_name = 'Direk Gönder'
    verbose_name_plural = 'Direk Gönder'



class AdminSiparisler(admin.ModelAdmin):
    inlines = [YuklenecekSiparislerInline,DirekGonderInline]
    list_display = ("id","Numara","Operator","PaketAdi","SanalTutar","OperatorTip","PaketKupur","Durum","BayiAciklama","ManuelApi","gecen_sure",)
    search_fields = ("Numara",)
    list_editable = ("Durum","ManuelApi","BayiAciklama")
    list_filter = ("OperatorTip","Durum",)
    readonly_fields = ('PaketKupur',)#tam ortada 'SorguPaketID',    'Aciklama',

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Sadece "İşlemde", "Askıda" ve "Alternatif Paketler Deneniyor" durumunda olan siparişleri göster
        durumlar = [Durumlar.ISLEMDE, Durumlar.askida, Durumlar.ALTERNATIF_DENEYEN]
        queryset = queryset.filter(Durum__in=durumlar)
        # Sadece "Durum" sütununda bulunan siparişleri göster
        queryset = queryset.exclude(Durum=None)
        return queryset

    actions = ["tamamlandi_action","BeklemeyeAL_action","iptalEt_action"]



    def tamamlandi_action(self, request, queryset):

        for siparis in queryset:
            user = request.user

            guncel_aciklama = siparis.Aciklama or ""
            GelenApi = siparis.ManuelApi.Apiadi if siparis.ManuelApi else ""

            yeni_aciklama = user.username +" _Tarafından_ " +GelenApi +" Apisinden <- Manuel Olarak Onaylandı\n "
            siparis.Aciklama = guncel_aciklama + yeni_aciklama
            siparis.Durum = 99  # Durum 99: Tamamlandı
            siparis.save()

        rows_updated = len(queryset)
        self.message_user(request, f"{rows_updated} sipariş güncellendi.")

    tamamlandi_action.short_description = "Seçilen Apiden Düşerek Onayla"


    def BeklemeyeAL_action(self, request, queryset):
        for siparis in queryset:
            user = request.user

            guncel_aciklama = siparis.Aciklama or ""
            GelenApi = siparis.ManuelApi.Apiadi if siparis.ManuelApi else ""


            yeni_aciklama = user.username +" _Tarafından_ " +GelenApi +" Apisinden <- Beklemeye Alındı\n "
            siparis.Aciklama = guncel_aciklama + yeni_aciklama
            siparis.Durum = 1  # Durum 99: Tamamlandı
            siparis.save()

        rows_updated = len(queryset)
        self.message_user(request, f"{rows_updated} sipariş Beklemeye Alındı.")
    BeklemeyeAL_action.short_description = "Beklemeye Al"

    def iptalEt_action(self, request, queryset):
        for siparis in queryset:
            user = request.user

            guncel_aciklama = siparis.Aciklama or ""
            GelenApi = siparis.ManuelApi.Apiadi if siparis.ManuelApi else ""

            yeni_aciklama = user.username +" _Tarafından_ " +GelenApi +" Apisinden <- iptale Alındı\n "
            siparis.Aciklama = guncel_aciklama + yeni_aciklama
            siparis.Durum = 97  # Durum 99: Tamamlandı
            siparis.save()

        rows_updated = len(queryset)
        self.message_user(request, f"{rows_updated} sipariş iptalle Alındı.")
    iptalEt_action.short_description = "siparişleri iptal Et"

    def has_delete_permission(self, request, obj=None):
        return True

    def gecen_sure(self, obj):
        suanki_zaman = timezone.now()
        gecen_zaman = suanki_zaman - obj.OlusturmaTarihi
        return '{:.0f} saniye'.format(gecen_zaman.total_seconds())

    gecen_sure.short_description = 'Geçen Süre'


class AdminAnaOperator(admin.ModelAdmin):
    list_display = ("id","AnaOperatorler",)

class AdminAltOperator(admin.ModelAdmin):
    list_display = ("id","AltOperatorler",)


class AdminKategoriListesi(admin.ModelAdmin):
    list_display = ("id","GorunecekName","KategoriAdi","Operatoru","KategoriAltOperatoru","GorunecekSira","Aktifmi",)
    list_editable = ("KategoriAdi","Operatoru","KategoriAltOperatoru","GorunecekSira","Aktifmi",)



class VodafoneSesInline(admin.TabularInline):
    model = VodafonePaketler
    extra = 1
class TurkcellInline(admin.TabularInline):
    model = Turkcell
    extra = 1


def add_all_kontors_to_api(modeladmin, request, queryset):
    for api in queryset:
        kontor_listesi = KontorList.objects.filter(Kategorisi__in=[1, 2])
        for kontor in kontor_listesi:
            if not Turkcell.objects.filter(apiler=api, urun_adi=kontor.Urun_adi, kupur=kontor.Kupur, eslestirme_kupur=kontor.Kupur).exists():
                Turkcell.objects.create(
                    apiler=api,
                    urun_adi=kontor.Urun_adi,
                    kupur=kontor.Kupur,
                    eslestirme_kupur=kontor.Kupur
                )

add_all_kontors_to_api.short_description = "Seçilen API'ye turkcell operatöründeki tüm kontörleri ekle"


def add_Vodafone_kontors_to_api(modeladmin, request, queryset):
   # eslestirme_operator_adi = input("Eşleştirme operator adı: ")
    for api in queryset:
        apituru = api.ApiTuru
        SecilenApi = apituru.ApiYazilimAdi

        print(api.ApiTuru)
        print(type(api.ApiTuru))
        kontor_listesi = KontorList.objects.filter(Kategorisi__in=[3])
        for kontor in kontor_listesi:
            if not VodafonePaketler.objects.filter(apiler=api, urun_adi=kontor.Urun_adi, kupur=kontor.Kupur, eslestirme_kupur=kontor.Kupur).exists():

                if SecilenApi == "Znet":
                    VodafonePaketler.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi="vodafone",
                        eslestirme_operator_tipi="ses",
                        eslestirme_kupur=kontor.zNetKupur
                    )
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    VodafonePaketler.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi=GelenRef[0],
                        eslestirme_operator_tipi=GelenRef[1],
                        eslestirme_kupur=kontor.Kupur
                    )
                else:
                    print("Nasip Patladık.")

add_Vodafone_kontors_to_api.short_description = "Seçilen API'ye Vodafone operatöründeki tüm kontörleri ekle"



def delete_turkcell(modeladmin, request, queryset):
    for api in queryset:
        api.turkcell_set.all().delete()
    modeladmin.message_user(request, "Seçilen apilere ait tüm Turkcell kayıtları silindi.")


delete_turkcell.short_description = "Seçilen API'lerin Turkcell kayıtlarını sil"

def delete_vodafone(modeladmin, request, queryset):
    for api in queryset:
        api.vodafonepaketler_set.all().delete()
    modeladmin.message_user(request, "Seçilen apilere ait tüm Vodafone kayıtları silindi.")


delete_vodafone.short_description = "Seçilen API'lerin Vodafone kayıtlarını sil"

class ApilerAdminForm(forms.ModelForm):
    class Meta:
        model = Apiler
        fields = '__all__'
        widgets = {
            'Sifre': PasswordInput(render_value=True),
        }
class AdminApiListesi(admin.ModelAdmin):
    form = ApilerAdminForm
    list_display = ("id","Apiadi","ApiBakiye","ApiTanim","ApiAktifmi","HataManuel",)
    list_editable = ("ApiBakiye","ApiAktifmi","ApiTanim","HataManuel",)

    def toplam_kontor(self, obj):
        return "{:,.0f}".format(obj.kontor_list.toplam_kontor())

    toplam_kontor.short_description = 'Toplam Kontor'

    inlines = [TurkcellInline,VodafoneSesInline]
    actions = [add_all_kontors_to_api,delete_turkcell,add_Vodafone_kontors_to_api,delete_vodafone]

class AdminApiKagetori(admin.ModelAdmin):
    list_display = ("id","ApiYazilimAdi",)
@admin.register(Bayi_Listesi)
class Bayi_Bakiyeleri(admin.ModelAdmin):
    list_display = ('user', 'Bayi_Bakiyesi')

@admin.register(BakiyeHareketleri)
class BakiyeHareketleriAdmin(admin.ModelAdmin):
    list_display = ('user', 'islem_tutari', 'onceki_bakiye', 'sonraki_bakiye', 'tarih', 'aciklama')



admin.site.register(Durumlar,DurumlarAdmin)
admin.site.register(AnaOperator,AdminAnaOperator)
admin.site.register(AltOperator,AdminAltOperator)
admin.site.register(KontorList,AdminKontorListesi)
admin.site.register(Siparisler,AdminSiparisler)
admin.site.register(ApiKategori,AdminApiKagetori)
admin.site.register(Kategori,AdminKategoriListesi)
admin.site.register(Apiler,AdminApiListesi)


