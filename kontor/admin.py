from django.contrib import admin
from .models import KontorList,Kategori,Apiler,ApiKategori,Banka,AlternativeProduct,Siparisler,AnaOperator,AltOperator,YuklenecekSiparisler,Durumlar,Turkcell,ApidenCekilenPaketler,VodafonePaketler,Bayi_Listesi,BakiyeHareketleri,TTses,TTtam,FiyatGuruplari,Fiyatlar
from django.utils.html import format_html
from django.urls import reverse,path
from django.utils import timesince,timezone
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.forms import Select, RadioSelect, PasswordInput

from django.contrib.auth.models import User
from .urunleri_cek import *
from .forms import *
from django import forms
import os




# Register your models here.
class DurumlarAdmin(admin.ModelAdmin):
    list_display = ['durum_id', 'get_durum_id_display']

class AlternativeProductInline(admin.TabularInline):
    model = AlternativeProduct
    extra = 1
    verbose_name_plural = "Alternatif ürünler"



class AdminBanka(admin.ModelAdmin):
    list_display = ('banka_adi', 'hesap_sahibi', 'bakiye','BayiGormesin','Aktifmi')
    readonly_fields = ('bakiye',)

class AdminApidenCekilenPaketler(admin.ModelAdmin):
    list_display = ('apiler', 'urun_adi', 'kupur','ApiGelen_fiyati','ApiGelen_operator_adi','ApiGelen_operator_tipi')












class AdminKontorListesi(admin.ModelAdmin):
    list_display = ("id","Kupur","Urun_adi","MaliyetFiyat","SatisFiyat","Aktifmi","api1","api2","api3", "alternatif_urunler_count",)#"alternatif_urunler",
    list_editable = ("Urun_adi","Aktifmi","MaliyetFiyat","SatisFiyat","api1","api2","api3",)
    search_fields = ("Urun_adi","Kupur",)
    list_filter = ("Kategorisi",)
    inlines = [AlternativeProductInline]

    actions = ['otoyap_action','TumAlternetifiSil_action',"redirect_to_form"]

    def redirect_to_form(self, request, queryset):
        selected = queryset.values_list('id', flat=True)
        return HttpResponseRedirect(f"/change_api?ids={','.join(str(id) for id in selected)}")

    redirect_to_form.short_description = "API Değiştir"

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
    list_display = ("id","Numara","PaketAdi","SanalTutar","Operator","OperatorTip","PaketKupur","Durum","BayiAciklama","OlusturmaTarihi","gecen_sure",)
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


    #TODO iptal et bölümünde bakiye iadesi + basairli ise api bakiyesi iadesi de lazım.
    def iptalEt_action(self, request, queryset):
        for siparis in queryset:
            user = request.user

            guncel_aciklama = siparis.Aciklama or ""
            GelenApi = siparis.ManuelApi.Apiadi if siparis.ManuelApi else ""
            iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)

            yeni_aciklama = user.username +" _Tarafından_ " +GelenApi +" Apisinden <- iptale Alındı\n "
            siparis.Aciklama = guncel_aciklama + yeni_aciklama
            siparis.Durum = iptal
            siparis.save()

        rows_updated = len(queryset)
        self.message_user(request, f"{rows_updated} sipariş iptalle Alındı.")

    iptalEt_action.short_description = "siparişleri iptal Et"


    #TODO Sipariş Silme Kapatma!
    def has_delete_permission(self, request, obj=None):
        return False

    def gecen_sure(self, obj):
        if obj.SonucTarihi:
            gecen_zaman = obj.SonucTarihi - obj.OlusturmaTarihi
            return '{:.0f} saniye'.format(gecen_zaman.total_seconds())
        else:
            return 'devam ediyor'

    gecen_sure.short_description = 'Geçen Süre'


class AdminAnaOperator(admin.ModelAdmin):
    list_display = ("id","AnaOperatorler",)

class AdminAltOperator(admin.ModelAdmin):
    list_display = ("id","AltOperatorler",)


class AdminKategoriListesi(admin.ModelAdmin):
    list_display = ("id","GorunecekName","KategoriAdi","Operatoru","KategoriAltOperatoru","GorunecekSira","Aktifmi",)
    list_editable = ("KategoriAdi","Operatoru","KategoriAltOperatoru","GorunecekSira","Aktifmi",)



#class VodafoneSesInlineForm(forms.ModelForm):
#    class Meta:
#        model = VodafonePaketler
#        exclude = []
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#        apiden_gelenler = self.fields['Apiden_gelenler']
#        apiden_gelenler.empty_label = '-Paket Seçiniz.'
#
#        if self.instance and self.instance.eslestirme_kupur:
#            apiden_gelenler.queryset = apiden_gelenler.queryset.filter(kupur=self.instance.eslestirme_kupur)
#            apiden_gelenler.empty_label = None
#
#        apiden_gelenler.label_from_instance = lambda obj: f"{obj.urun_adi} ({obj.kupur})"
#
#    def save(self, commit=True):
#        vodafone_paketler = super().save(commit=False)
#        if vodafone_paketler.Apiden_gelenler:
#            apiden_gelenler = vodafone_paketler.Apiden_gelenler
#            eslestirme_kupur = apiden_gelenler.kupur
#            api_gelen_fiyat = apiden_gelenler.ApiGelen_fiyati
#            vodafone_paketler.eslestirme_kupur = eslestirme_kupur
#            vodafone_paketler.alis_fiyati = api_gelen_fiyat
#        if commit:
#            vodafone_paketler.save()
#        return vodafone_paketler





#class VodafoneSesInlineForm(forms.ModelForm):
#    class Meta:
#        model = VodafonePaketler
#        exclude = []
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#        apiden_gelenler = self.fields['Apiden_gelenler']
#        apiden_gelenler.empty_label = '-Paket Seçiniz.'
#
#        if self.instance and self.instance.eslestirme_kupur:
#            apiden_gelenler.queryset = apiden_gelenler.queryset.filter(kupur=self.instance.eslestirme_kupur)
#            apiden_gelenler.empty_label = None
#
#        apiden_gelenler.label_from_instance = lambda obj: f"{obj.urun_adi} ({obj.kupur})"
#
#    def save(self, commit=True):
#        vodafone_paketler = super().save(commit=False)
#        if vodafone_paketler.Apiden_gelenler:
#            apiden_gelenler = vodafone_paketler.Apiden_gelenler
#            eslestirme_kupur = apiden_gelenler.kupur
#            api_gelen_fiyat = apiden_gelenler.ApiGelen_fiyati
#            vodafone_paketler.eslestirme_kupur = eslestirme_kupur
#            vodafone_paketler.alis_fiyati = api_gelen_fiyat
#        if commit:
#            vodafone_paketler.save()
#        return vodafone_paketler



#TODO çalışan bu
#class VodafoneSesInlineForm(forms.ModelForm):
#    class Meta:
#        model = VodafonePaketler
#        exclude = []
#
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#
#        apiden_gelenler = self.fields['Apiden_gelenler']
#        apiden_gelenler.empty_label = '-Paket Seçiniz.'
#
#        if self.instance and self.instance.eslestirme_kupur:
#            apiden_gelenler.queryset = apiden_gelenler.queryset.filter(kupur=self.instance.eslestirme_kupur)
#            #apiden_gelenler.queryset = apiden_gelenler.queryset.filter(kupur=self.instance.eslestirme_kupur, apiler=self.instance.apiler)
#            #apiden_gelenler.empty_label = None
#        else:
#            apiden_gelenler.queryset = apiden_gelenler.queryset.none()
#
#        apiden_gelenler.label_from_instance = lambda obj: f"{obj.urun_adi} ({obj.kupur})"
#
#    def save(self, commit=True):
#        vodafone_paketler = super().save(commit=False)
#        if vodafone_paketler.Apiden_gelenler:
#            apiden_gelenler = vodafone_paketler.Apiden_gelenler
#            eslestirme_kupur = apiden_gelenler.kupur
#            api_gelen_fiyat = apiden_gelenler.ApiGelen_fiyati
#            vodafone_paketler.eslestirme_kupur = eslestirme_kupur
#            vodafone_paketler.alis_fiyati = api_gelen_fiyat
#        if commit:
#            vodafone_paketler.save()
#        return vodafone_paketler
class VodafoneSesInlineForm(forms.ModelForm):
    class Meta:
        model = VodafonePaketler
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        apiden_gelenler = self.fields['Apiden_gelenler']
        apiden_gelenler.empty_label = '-Paket Seçiniz.'

        if self.instance and self.instance.eslestirme_kupur:
            apiden_gelenler.queryset = apiden_gelenler.queryset.filter(kupur=self.instance.eslestirme_kupur)
            apiden_gelenler.empty_label = None

        apiden_gelenler.label_from_instance = lambda obj: f"{obj.urun_adi} ({obj.kupur})"

    def save(self, commit=True):
        vodafone_paketler = super().save(commit=False)
        if vodafone_paketler.Apiden_gelenler:
            apiden_gelenler = vodafone_paketler.Apiden_gelenler
            eslestirme_kupur = apiden_gelenler.kupur
            api_gelen_fiyat = apiden_gelenler.ApiGelen_fiyati
            vodafone_paketler.eslestirme_kupur = eslestirme_kupur
            vodafone_paketler.alis_fiyati = api_gelen_fiyat
        if commit:
            vodafone_paketler.save()
        return vodafone_paketler

class VodafoneSesInline(admin.TabularInline):
    model = VodafonePaketler
    extra = 1
    form = VodafoneSesInlineForm



class TurkcellInline(admin.TabularInline):
    model = Turkcell
    extra = 1
class TTsesInline(admin.TabularInline):
    model = TTses
    extra = 1
class TTtamInline(admin.TabularInline):
    model = TTtam
    extra = 1



class FiyatlarForm(forms.ModelForm):
    class Meta:
        model = Fiyatlar
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['Operatoru'].queryset = AnaOperator.objects.filter(id=self.instance.Operatoru.id)



class FiyatlarInlines(admin.TabularInline):
    model = Fiyatlar
    form = FiyatlarForm
    extra = 1



def TTSES_Paketleri_Ekle(modeladmin, request, queryset):
    for api in queryset:
        apituru = api.ApiTuru
        SecilenApi = apituru.ApiYazilimAdi
        kontor_listesi = KontorList.objects.filter(Kategorisi__in=[4])
        for kontor in kontor_listesi:
            #if not TTses.objects.filter(apiler=api, kupur=kontor.Kupur).exists():
            GelenPaketler = TTses.objects.filter(apiler=api, kupur=kontor.Kupur)
            if GelenPaketler.exists():
                PaketiGuncelle = GelenPaketler.first()
                if SecilenApi == "Znet":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = "avea"
                    PaketiGuncelle.eslestirme_operator_tipi = "ses"
                    PaketiGuncelle.eslestirme_kupur = kontor.Kupur
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = GelenRef[0]
                    PaketiGuncelle.eslestirme_operator_tipi = GelenRef[1]
                    PaketiGuncelle.eslestirme_kupur = kontor.zNetKupur
                elif SecilenApi == "grafi":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                PaketiGuncelle.save()
            else:
                if SecilenApi == "Znet":
                    TTses.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi="avea",
                        eslestirme_operator_tipi="ses",
                        eslestirme_kupur=kontor.Kupur
                    )
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    TTses.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi=GelenRef[0],
                        eslestirme_operator_tipi=GelenRef[1],
                        eslestirme_kupur=kontor.Kupur
                    )
                elif SecilenApi == "grafi":
                    TTses.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_kupur=0
                    )
                else:
                    print("Nasip Patladık.")

TTSES_Paketleri_Ekle.short_description = "Seçilen API'ye TTSes operatöründeki tüm kontörleri ekle"

def Turkcell_Paketleri_Ekle(modeladmin, request, queryset):
    for api in queryset:
        apituru = api.ApiTuru
        SecilenApi = apituru.ApiYazilimAdi
        print(api.ApiTuru)
        print(type(api.ApiTuru))
        kontor_listesi = KontorList.objects.filter(Kategorisi__in=[1])
        for kontor in kontor_listesi:
            #if not Turkcell.objects.filter(apiler=api, kupur=kontor.Kupur).exists():
            GelenPaketler = Turkcell.objects.filter(apiler=api, kupur=kontor.Kupur)
            if GelenPaketler.exists():
                PaketiGuncelle = GelenPaketler.first()
                if SecilenApi == "Znet":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = "turkcell"
                    PaketiGuncelle.eslestirme_operator_tipi = "ses"
                    PaketiGuncelle.eslestirme_kupur = kontor.Kupur
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = GelenRef[0]
                    PaketiGuncelle.eslestirme_operator_tipi = GelenRef[1]
                    PaketiGuncelle.eslestirme_kupur = kontor.Kupur
                elif SecilenApi == "grafi":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                PaketiGuncelle.save()
            else:
                if SecilenApi == "Znet":
                    Turkcell.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi="turkcell",
                        eslestirme_operator_tipi="ses",
                        eslestirme_kupur=kontor.Kupur
                    )
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    Turkcell.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        eslestirme_operator_adi=GelenRef[0],
                        eslestirme_operator_tipi=GelenRef[1],
                        eslestirme_kupur=kontor.Kupur
                    )
                    Turkcell.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                    )
                elif SecilenApi == "grafi":
                    pass
                else:
                    print("Nasip Patladık.")

Turkcell_Paketleri_Ekle.short_description = "Seçilen API'ye turkcell operatöründeki tüm kontörleri ekle"


def Vodafonel_Paketleri_Ekle(modeladmin, request, queryset):
   # eslestirme_operator_adi = input("Eşleştirme operator adı: ")
    for api in queryset:
        apituru = api.ApiTuru
        SecilenApi = apituru.ApiYazilimAdi

        print(api.ApiTuru)
        print(type(api.ApiTuru))
        kontor_listesi = KontorList.objects.filter(Kategorisi__in=[3])
        for kontor in kontor_listesi:
            #if not VodafonePaketler.objects.filter(apiler=api, kupur=kontor.Kupur).exists():
            GelenPaketler = VodafonePaketler.objects.filter(apiler=api, kupur=kontor.Kupur)
            if GelenPaketler.exists():
                PaketiGuncelle = GelenPaketler.first()
                if SecilenApi == "Znet":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = "vodafone"
                    PaketiGuncelle.eslestirme_operator_tipi = "ses"
                    PaketiGuncelle.eslestirme_kupur = kontor.zNetKupur
                elif SecilenApi == "Gencan":
                    GelenRef = str(api.ApiTanim).split(",")
                    print(GelenRef)
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_operator_adi = GelenRef[0]
                    PaketiGuncelle.eslestirme_operator_tipi = GelenRef[1]
                    PaketiGuncelle.eslestirme_kupur = kontor.zNetKupur
                elif SecilenApi == "grafi":
                    PaketiGuncelle.apiler = api
                    PaketiGuncelle.urun_adi = kontor.Urun_adi
                    PaketiGuncelle.kupur = kontor.Kupur
                    PaketiGuncelle.eslestirme_kupur = kontor.zNetKupur
                PaketiGuncelle.save()
            else:
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
                elif SecilenApi == "grafi":
                    VodafonePaketler.objects.create(
                        apiler=api,
                        urun_adi=kontor.Urun_adi,
                        kupur=kontor.Kupur,
                        #eslestirme_operator_adi="vodafone",
                        #eslestirme_operator_tipi="ses",
                        eslestirme_kupur=0
                    )
                else:
                    print("Nasip Patladık.")

Vodafonel_Paketleri_Ekle.short_description = "Seçilen API'ye Vodafone operatöründeki tüm kontörleri ekle"

def PaketleriCek(modeladmin, request, queryset):
    for api in queryset:
        apituru = api.ApiTuru
        SecilenApi = apituru.ApiYazilimAdi
        if SecilenApi=="grafi":
            paketler = paketlericekgrafi(api,api.SiteAdresi,api.Kullanicikodu,api.Kullaniciadi,api.Sifre)
        elif SecilenApi == "Gencan":
            paketler = paketlericekGenco(api, api.SiteAdresi, api.Kullanicikodu, api.Kullaniciadi, api.Sifre)

PaketleriCek.short_description = "Seçilen API'lerin PaketleriniCek"

def delete_turkcell(modeladmin, request, queryset):
    for api in queryset:
        api.turkcell_set.all().delete()
    modeladmin.message_user(request, "Seçilen apilere ait tüm Turkcell kayıtları silindi.")
delete_turkcell.short_description = "Seçilen API'lerin Turkcell kayıtlarını sil"

def delete_ttses(modeladmin, request, queryset):
    for api in queryset:
        api.TTses_set.all().delete()
    modeladmin.message_user(request, "Seçilen apilere ait tüm TTSes kayıtları silindi.")
delete_ttses.short_description = "Seçilen API'lerin TTSes kayıtlarını sil"

def delete_TTtam(modeladmin, request, queryset):
    for api in queryset:
        api.TTtam_set.all().delete()
    modeladmin.message_user(request, "Seçilen apilere ait tüm TTtam kayıtları silindi.")
delete_TTtam.short_description = "Seçilen API'lerin TTtam kayıtlarını sil"

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
    list_display = ("id","Apiadi","ApiBakiye","ApiTanim","ApiAktifmi","RefNumarasi","HataManuel",)
    list_editable = ("ApiBakiye","ApiAktifmi","ApiTanim","RefNumarasi","HataManuel",)


    def toplam_kontor(self, obj):
        return "{:,.0f}".format(obj.kontor_list.toplam_kontor())

    toplam_kontor.short_description = 'Toplam Kontor'

    inlines = [TurkcellInline,VodafoneSesInline,TTsesInline,TTtamInline]
    actions = [PaketleriCek,Vodafonel_Paketleri_Ekle,Turkcell_Paketleri_Ekle,TTSES_Paketleri_Ekle,delete_turkcell,delete_ttses,delete_TTtam,delete_vodafone]

class AdminApiKagetori(admin.ModelAdmin):
    list_display = ("id","ApiYazilimAdi",)



class AdminFiyatlar(admin.ModelAdmin):
    list_display = ("id","FiyatKategorisi","OzelApi")
    list_editable = ("FiyatKategorisi","OzelApi")
    inlines = [FiyatlarInlines]
    actions = ["veri_aktar"]

    def veri_aktar(modeladmin, request, queryset):
        # İlk olarak, operatörleri ve karşılık gelen Kategori örneklerini bir sözlükte tanımlayın

        for FiyatlarCekildi in queryset:

            FiyatGrubu = FiyatlarCekildi.id
            FiyatGrubu = Fiyatlar.objects.get(id=FiyatGrubu)



            gelenAnaOperator = AnaOperator.objects.get(pk=int(3))

            kontor_listesi = KontorList.objects.filter(Kategorisi__in=[3])
            for kontor in kontor_listesi:
                GelenPaketler = Fiyatlar.objects.filter(fiyat_grubu=FiyatGrubu,Kupur=kontor.Kupur)
                if GelenPaketler.exists():
                    FiyatlariGuncelle = GelenPaketler.first()
                    FiyatlariGuncelle.PaketAdi = kontor.Urun_adi
                    FiyatlariGuncelle.Maliyet = kontor.MaliyetFiyat
                    FiyatlariGuncelle.save()
                else:
                    Fiyatlar.objects.create(
                        fiyat_grubu = FiyatGrubu ,
                        Operatoru = gelenAnaOperator,
                        Kupur = kontor.Kupur,
                        PaketAdi = kontor.Urun_adi,
                        Maliyet = kontor.MaliyetFiyat,
                        BayiSatisFiyati = 0,
                        Kar = 0,
                    )




    veri_aktar.short_description = "Seçili fiyat grupları için veri aktar"


@admin.register(Bayi_Listesi)
class Bayi_Bakiyeleri(admin.ModelAdmin):
    list_display = ('user', 'Bayi_Bakiyesi','Borc')
    readonly_fields = ('user','Bayi_Bakiyesi','Borc')



@admin.register(BakiyeHareketleri)
class BakiyeHareketleriAdmin(admin.ModelAdmin):
    list_display = ('user', 'islem_tutari', 'onceki_bakiye', 'sonraki_bakiye', 'onceki_Borc', 'sonraki_Borc','tarih', 'aciklama')
    readonly_fields = ('user', 'islem_tutari', 'onceki_bakiye', 'sonraki_bakiye', 'onceki_Borc', 'sonraki_Borc','tarih', 'aciklama')


admin.site.register(Durumlar,DurumlarAdmin)
admin.site.register(Banka,AdminBanka)
admin.site.register(ApidenCekilenPaketler,AdminApidenCekilenPaketler)
admin.site.register(AnaOperator,AdminAnaOperator)
admin.site.register(AltOperator,AdminAltOperator)
admin.site.register(KontorList,AdminKontorListesi)
admin.site.register(Siparisler,AdminSiparisler)
admin.site.register(ApiKategori,AdminApiKagetori)
admin.site.register(Kategori,AdminKategoriListesi)
admin.site.register(Apiler,AdminApiListesi)
admin.site.register(FiyatGuruplari,AdminFiyatlar)