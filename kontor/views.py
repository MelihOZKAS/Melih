from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,Durumlar
import requests
from decimal import Decimal
from .kontrol import *
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


@csrf_exempt
def ApiSiparisKaydet(request):
    Sonuc = ApiZnetSiparisKaydet(request)
    return HttpResponse(Sonuc)
@csrf_exempt
def ApiSiparisSonuc(request):
    Sonuc = SonucKontrolGelen(request)
    return HttpResponse(Sonuc)
@csrf_exempt
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

@csrf_exempt
def VodafoneSesEkle (request):
    Sonuc = VodafonePaketleriCek(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def TurkcellSesEkle (request):
    Sonuc = TurkcellPaketleriCek(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def AnaKatEkle (request):
    Sonuc = AnaOperatorleriCek(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def AnaKatEkle (request):
    Sonuc = AnaOperatorleriEkleme(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def AltKatEkle (request):
    Sonuc = AltOperatorleriEkleme(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def OperatorEkle (request):
    Sonuc = OperatorEkleme(request)
    return HttpResponse(Sonuc)

@csrf_exempt
def ANaPaketGonder (request):
    Sonuc = AnaPaketGonder()
    return HttpResponse(Sonuc)




#def movies_details(request,slug):
#    return render(request,'movie-details.html',{"slug":slug})
from django.shortcuts import get_object_or_404

def update(request, pk):
    vodafone_paketler = get_object_or_404(VodafonePaketler, pk=pk)
    if request.method == 'POST':
        form = VodafoneSesInlineForm(request.POST, instance=vodafone_paketler)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = VodafoneSesInlineForm(instance=vodafone_paketler)
    return render(request, 'update.html', {'form': form})
