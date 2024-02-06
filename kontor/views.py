from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,Durumlar,GelenSMS
import requests
from decimal import Decimal
from .kontrol import *
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

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

def TelegramSend(request):
    Sonuc = GecikmeBildir()
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
def TTSesEkle (request):
    Sonuc = TTsesPaketleriCek(request)
    return HttpResponse(Sonuc)


@csrf_exempt
def AnaKatEkle (request):
    Sonuc = AnaOperatorleriCek(request)
    return HttpResponse(Sonuc)

#todo burada bi pok var.
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



def update_api(request):
    api1_id = request.GET.get('api1')
    api2_id = request.GET.get('api2')
    api3_id = request.GET.get('api3')
    ids = request.GET.get('ids', '')

    if ids:
        ids = ids.split(',')
        for id in ids:
            try:
                kontor = KontorList.objects.get(pk=int(id))
                if api1_id and api1_id != '':
                    kontor.api1 = Apiler.objects.get(pk=int(api1_id))
                elif api1_id == '':
                    kontor.api1 = None
                if api2_id and api2_id != '':
                    kontor.api2 = Apiler.objects.get(pk=int(api2_id))
                elif api2_id == '':
                    kontor.api2 = None
                if api3_id and api3_id != '':
                    kontor.api3 = Apiler.objects.get(pk=int(api3_id))
                elif api3_id == '':
                    kontor.api3 = None
                kontor.save()
            except ValueError:
                pass  # invalid id, ignore
            except KontorList.DoesNotExist:
                pass  # kontor object not found, ignore
            except Apiler.DoesNotExist:
                pass  # api object not found, ignore

    return HttpResponseRedirect('/admin/kontor/kontorlist/')







@csrf_exempt
def SmsYakala(request):
    if request.method == 'POST':
        sahibi = request.POST['sahibi']
        gonderen = request.POST['gonderen']
        mesaj = request.POST['mesaj']

        gelen_mesa_parcali = mesaj.split(" ")
        mesaj_ilk = gelen_mesa_parcali[0]

        mesaj_yeni = mesaj.replace(",", "")

        if gonderen == 'FUPS' and mesaj_ilk in ['3D', 'Son', 'İlk'] or mesaj_ilk in ['in', 'risini', 'Son', 'Sonu', 'İlk']:
            return HttpResponse("Basarili")

        else:
            try:
                GelenSMS.objects.create(numara=sahibi, banka=gonderen, mesaj=mesaj_yeni)
                return HttpResponse("Basarili")
            except Exception as e:
                return HttpResponse("DB ye kaydedemedim.")
    else:
        return HttpResponse("Hatalı İşlem")


@csrf_exempt
def sms_getir(request):
    if request.method == 'POST':
        numarasi = request.POST.get('numarasi')
        if numarasi:
            smsler = GelenSMS.objects.filter(numara=numarasi).order_by('-id')[:10]
            if smsler.exists():
                sonuc = "|".join([f"{sms.id},{sms.banka},{sms.mesaj}" for sms in smsler])
                return HttpResponse(sonuc)
            else:
                return HttpResponse("SonucMesajYok!")
        else:
            return HttpResponse("Numara bulunamadı!")
    else:
        return HttpResponse({"SonucHatali"})




@csrf_exempt
def sms_getir_get(request):
    python = request.GET.get('Python', '')
    if python == 'SukurlerOlsun':
        numarasi = request.GET.get('numarasi', '')
        smsler = GelenSMS.objects.filter(numara=numarasi).order_by('-id')[:10]
        if smsler.exists():
            sonuc = "<br>".join([f"{sms.id},{sms.banka},{sms.mesaj}" for sms in smsler])
            return HttpResponse(sonuc)
        else:
            return HttpResponse({"Sonuc": "MesajYok!"})
    else:
        return HttpResponse({"Sonuc": "Hatali"})




@require_GET
def sitelinki(request):
    return HttpResponse(ads_content, content_type="text/plain")

ads_content = """185.92.2.178:4444"""