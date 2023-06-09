from django.urls import path
from . import views



urlpatterns = [
    #path("",views.index),
    #path("movies",views.movies),
    #path("movies/<slug:slug>",views.movies_details),
    #path("bayi_panel",views.bayi_panel),
    #path("bayi_operator_sec/",views.bayi_panel_operatorsec),
    #path("bayi_operator_altKategori/",views.bayi_Operator_AltKategori),
    #path("bayi_Game_sec/",views.bayi_panel_gamesec),
    #path("bayi_panel_yeni",views.bayi_panel_yeni),
    #path("tetik",views.Tetik),
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
    path('change_api/', views.change_api, name='change_api'),
    path('update_api', views.update_api, name='update_api'),


    #path('', views.bayi_view, name='bayi'),
    #Nasip
]