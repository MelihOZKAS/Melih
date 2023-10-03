from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,Durumlar,GelenSMS
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








def SmsYakala(request):
    if request.method == 'POST':
        android = request.POST.get('Android', '')
        if android == 'SMSGonder':
            sahibi = request.POST.get('sahibi', '')
            gonderen = request.POST.get('gonderen', '')
            mesaj = request.POST.get('mesaj', '')

            gelen_mesa_parcali = mesaj.split(" ")
            mesaj_ilk = gelen_mesa_parcali[0]

            mesaj_yeni = mesaj.replace(",", "")

            if gonderen == 'FUPS' and mesaj_ilk in ['3D', 'Son', 'İlk']:
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
        python = request.POST.get('Python', '')
        if python == 'SukurlerOlsun':
            numarasi = request.POST.get('numarasi', '')
            smsler = GelenSMS.objects.filter(numara=numarasi).order_by('-id')[:10]
            if smsler.exists():
                sonuc = "|".join([f"{sms.id},{sms.banka},{sms.mesaj}" for sms in smsler])
                return HttpResponse("Basarili")
            else:
                return HttpResponse("Sonuc : MesajYok!")
    else:
        return HttpResponse({"Sonuc": "Hatali"})




@csrf_exempt
def sms_getir_get(request):
    python = request.GET.get('Python', '')
    if python == 'SukurlerOlsun':
        numarasi = request.GET.get('numarasi', '')
        smsler = GelenSMS.objects.filter(numara=numarasi).order_by('-id')[:10]
        if smsler.exists():
            sonuc = "|".join([f"{sms.id},{sms.banka},{sms.mesaj}" for sms in smsler])
            return HttpResponse(sonuc)
        else:
            return HttpResponse({"Sonuc": "MesajYok!"})
    else:
        return HttpResponse({"Sonuc": "Hatali"})



#def movies_details(request,slug):
#    return render(request,'movie-details.html',{"slug":slug})
from django.shortcuts import get_object_or_404

#def update(request, pk):
#    vodafone_paketler = get_object_or_404(VodafonePaketler, pk=pk)
#    if request.method == 'POST':
#        form = VodafoneSesInlineForm(request.POST, instance=vodafone_paketler)
#        if form.is_valid():
#            form.save()
#            return redirect('index')
#    else:
#        form = VodafoneSesInlineForm(instance=vodafone_paketler)
#    return render(request, 'update.html', {'form': form})
#