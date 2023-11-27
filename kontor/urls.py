from django.urls import path
from . import views



urlpatterns = [

    path("sms-yakala",views.SmsYakala),
    path("sms-cek",views.sms_getir),
    path("sms-cek-get",views.sms_getir_get),
    path("servis/tl_servis.php",views.ApiSiparisKaydet),
    path("servis/tl_kontrol.php",views.ApiSiparisSonuc),
    path("PaketEkle",views.PaketEkleDB),
    path("alternatif",views.AlternatifKontrolET),
    path("organize",views.AlternatifYuklemeSirasi),
    path("alternatifHazirla",views.AlternatifYuklemeyeHazirla),
    path("sorguyagonder",views.SorguyaAt),
    path("sorgusonucu",views.SorguSonuc),
    path("alternatifgonder",views.alternatfgonder),
    path("alternatfsonuckontrol",views.alternatfsonucKontrol),
    path("anapaketsonuckontrol", views.AnaPakettsonucKontrol),
    path("VodafonePaketEkle", views.VodafoneSesEkle),
    path("TurkcellPaketEkle", views.TurkcellSesEkle),
    path("TTsesPaketEkle", views.TTSesEkle),
    path("anaKategoriEkle", views.AnaKatEkle),
    path("altKategoriEkle", views.AltKatEkle),
    path("OperatorEkle", views.OperatorEkle),
    path("AnaPaketGonder", views.ANaPaketGonder),
    path("TelegramSend", views.TelegramSend),
    path("siteadres", views.sitelinki),
    path('change_api/', views.change_api, name='change_api'),
    path('update_api', views.update_api, name='update_api'),


    #path('', views.bayi_view, name='bayi'),
    #Nasip
]