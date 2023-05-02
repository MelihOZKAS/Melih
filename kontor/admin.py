from django.contrib import admin
from .models import KontorList,Kategori,Apiler,ApiKategori,Banka,AlternativeProduct,Siparisler,AnaOperator,AltOperator,YuklenecekSiparisler,Durumlar,Turkcell,ApidenCekilenPaketler,VodafonePaketler,Bayi_Listesi,BakiyeHareketleri
from django.utils.html import format_html
from django.urls import reverse,path
from django.utils import timesince,timezone
from django.http import HttpResponseRedirect
from django.http import HttpResponse

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



class AdminBanka(admin.ModelAdmin):
    list_display = ('banka_adi', 'hesap_sahibi', 'bakiye','BayiGormesin','Aktifmi')



class AdminKontorListesi(admin.ModelAdmin):
    list_display = ("id","Kupur","Urun_adi","MaliyetFiyat","SatisFiyat","Aktifmi","api1","api2","api3", "alternatif_urunler_count",)#"alternatif_urunler",
    list_editable = ("Urun_adi","Aktifmi","MaliyetFiyat","SatisFiyat","api1","api2","api3",)
    search_fields = ("Urun_adi","Kupur",)
    list_filter = ("Kategorisi",)
    inlines = [AlternativeProductInline]

    actions = ['otoyap_action','TumAlternetifiSil_action']



    def otoyap_action(self, request, queryset):

        selected = queryset
        for obj in selected:
            alternatif_urunler = []
            AlternativeProduct.objects.filter(main_product=obj).delete()
            for urun in KontorList.objects.exclude(id=obj.id).order_by('MaliyetFiyat'):
                if urun.Aktifmi == True and urun.AlternatifYapilmasin == False and obj.AlternatifYapilmasin == False:
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
    def TumAlternetifiSil_action(self, request, queryset):

        selected = queryset
        for obj in selected:
            alternatif_urunler = []
            AlternativeProduct.objects.filter(main_product=obj).delete()
        self.message_user(request, "Seçilen Tüm Ürünlerin Alternatif listesi başarıyla silindi.")

    TumAlternetifiSil_action.short_description = "TumAlternetifiSil"

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

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import DateFieldListFilter





class DurumFilter(admin.SimpleListFilter):
    title = _('Durum')
    parameter_name = 'Durum'

    def lookups(self, request, model_admin):
        return (
            ('Basarili', _('Basarili')),
            ('Iptal', _('Iptal')),
            ('Islemde', _('Islemde')),
        )

    def queryset(self, request, queryset):
        AlternatifVarmiBaska = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderim_Bekliyor)
        AlternatifVarmiBaskagonder = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderimbekler)
        AnaPaketGoner = Durumlar.objects.get(durum_id=Durumlar.AnaPaketGoner)

        Alternatif_islemde = Durumlar.objects.get(durum_id=Durumlar.Alternatif_islemde)
        sorgusutamam = Durumlar.objects.get(durum_id=Durumlar.SorguTamam)
        ISLEMDE = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
        sorguda= Durumlar.objects.get(durum_id=Durumlar.Sorguda)
        sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
        AltKontrol = Durumlar.objects.get(durum_id=Durumlar.AltKontrol)
        aski = Durumlar.objects.get(durum_id=Durumlar.askida)
        Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)
        Basarili = Durumlar.objects.get(durum_id=Durumlar.Basarili)
        iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)
        ALTERNATIF_DENEYEN = Durumlar.objects.get(durum_id=Durumlar.ALTERNATIF_DENEYEN)
        AnaPaketSonucBekler = Durumlar.objects.get(durum_id=Durumlar.AnaPaketSonucBekler)
        Alternatif_Direk_Gonder = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Direk_Gonder)

        if self.value() == 'Basarili':
            return queryset.filter(Durum=Basarili)
        elif self.value() == 'Iptal':
            return queryset.filter(Durum=iptal)
        elif self.value() == 'Islemde':
            return queryset.filter(Durum__in=[Alternatif_Cevap_Bekliyor,Alternatif_Direk_Gonder,AnaPaketSonucBekler,AltKontrol,ALTERNATIF_DENEYEN,ISLEMDE, sorguda,aski,sorguCevap,sorgusutamam,Alternatif_Cevap_Bekliyor,Alternatif_islemde,AnaPaketGoner,AlternatifVarmiBaskagonder,AlternatifVarmiBaska])
           # return queryset.filter(Durum=Durumlar.ISLEMDE)


class AdminSiparisler(admin.ModelAdmin):
    inlines = [YuklenecekSiparislerInline,DirekGonderInline]
    list_display = ("id","Numara","PaketAdi","SanalTutar","Operator","OperatorTip","PaketKupur","Durum","BayiAciklama","ManuelApi","OlusturmaTarihi","gecen_sure",)
    search_fields = ("Numara",)
   # list_filter = ("Operator","Durum",)
    readonly_fields = ('PaketKupur',)#tam ortada 'SorguPaketID',    'Aciklama',
    date_hierarchy = 'OlusturmaTarihi'

    list_filter = (DurumFilter,('OlusturmaTarihi', DateFieldListFilter),)


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
        if obj.SonucTarihi:
            gecen_zaman = obj.SonucTarihi - obj.OlusturmaTarihi
            return '{:.0f} saniye'.format(gecen_zaman.total_seconds())
        else:
            return 'devam ediyor'

    gecen_sure.short_description = 'Geçen Süre'

    #def gecen_sure(self, obj):
    #    suanki_zaman = timezone.now()
    #    gecen_zaman = suanki_zaman - obj.OlusturmaTarihi
    #    return '{:.0f} saniye'.format(gecen_zaman.total_seconds())
#
    #gecen_sure.short_description = 'Geçen Süre'


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

    class Meta:
        model = Bayi_Listesi
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['secili_banka'].initial = None

@admin.register(BakiyeHareketleri)
class BakiyeHareketleriAdmin(admin.ModelAdmin):
    list_display = ('user', 'islem_tutari', 'onceki_bakiye', 'sonraki_bakiye', 'tarih', 'aciklama')



admin.site.register(Durumlar,DurumlarAdmin)
admin.site.register(Banka,AdminBanka)
admin.site.register(AnaOperator,AdminAnaOperator)
admin.site.register(AltOperator,AdminAltOperator)
admin.site.register(KontorList,AdminKontorListesi)
admin.site.register(Siparisler,AdminSiparisler)
admin.site.register(ApiKategori,AdminApiKagetori)
admin.site.register(Kategori,AdminKategoriListesi)
admin.site.register(Apiler,AdminApiListesi)


