from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,Durumlar
import requests
from decimal import Decimal
from .kontrol import AnaPaketGonder,ApiZnetSiparisKaydet,PaketEkle,AlternatifKontrol,\
    YuklenecekPaketler,AlternatifYuklemeyeHazirla,SorguyaGonder,SorguSonucKontrol,\
    AlternatifYuklemeGonder,AlternatifSonucKontrol,AnaPaketSonucKontrol
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
###
###
###
###
###def index(request):
###    return render(request,'index.html')
###def movies(request):
###    return render(request,'movies.html')
###def bayi_panel(request):
###    return render(request,'Yeniadam/tindex.html')
###def bayi_panel_yeni(request):
###    return render(request,'Bayi.html')
###def bayi_panel_operatorsec(request):
###    return render(request,'Bayi_Operator_Sec.html')
###def bayi_panel_gamesec(request):
###    return render(request,'Bayi_Game_Sec.html')
###def bayi_Operator_AltKategori(request):
###    return render(request,'Bayi_Operator_altKategori.html')
###def Tetik(request):
###    Sonuc = AnaPaketGonder()
###    return HttpResponse(Sonuc)

#def SiparisKontrol(request):
#    Sonuc = siparisGonder()
#    return HttpResponse(Sonuc)

def ApiSiparisKaydet(request):
    Sonuc = ApiZnetSiparisKaydet(request)
    return HttpResponse(Sonuc)

def AlternatifKontrolET(request):
    Sonuc = AlternatifKontrol(request)
    return HttpResponse(Sonuc)

def AlternatifYuklemeSirasi(request):
    Sonuc = YuklenecekPaketler(request)
    return HttpResponse(Sonuc)

def AlternatifyuklemeOncesi(request):
    Sonuc = AlternatifYuklemeyeHazirla(request)
    return HttpResponse(Sonuc)

def SorguyaAt(request):
    Sonuc = SorguyaGonder()
    return HttpResponse(Sonuc)

def SorguSonuc(request):
    Sonuc = SorguSonucKontrol()
    return HttpResponse(Sonuc)


def alternatfgonder(request):
    Sonuc = AlternatifYuklemeGonder()
    return HttpResponse(Sonuc)

def alternatfsonucKontrol(request):
    Sonuc = AlternatifSonucKontrol()
    return HttpResponse(Sonuc)
def AnaPakettsonucKontrol(request):
    Sonuc = AnaPaketSonucKontrol()
    return HttpResponse(Sonuc)


@csrf_exempt
def PaketEkleDB (request):
    Sonuc = PaketEkle(request)
    return HttpResponse(Sonuc)

#def movies_details(request,slug):
#    return render(request,'movie-details.html',{"slug":slug})
