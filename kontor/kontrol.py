import decimal

from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,AnaOperator,AltOperator,KontorList,Kategori,AlternativeProduct,YuklenecekSiparisler,Durumlar,VodafonePaketler,Bayi_Listesi,BakiyeHareketleri
import requests
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone

def AnaPaketGonder():
    AnaPaket = Durumlar.objects.get(durum_id=Durumlar.AnaPaketGoner)
    AnaPaketSonucBekler = Durumlar.objects.get(durum_id=Durumlar.AnaPaketSonucBekler)
    askida = Durumlar.objects.get(durum_id=Durumlar.askida)
   #Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)

    SiparisTum = Siparisler.objects.filter(Durum=AnaPaket)
    for Siparis in SiparisTum:
        if Siparis:
            if Siparis.Gonderim_Sirasi == 1:
                print("Girdim1")
                api = Siparis.api1
            if Siparis.Gonderim_Sirasi == 2:
                print("Girdim2")
                api = Siparis.api2
            if Siparis.Gonderim_Sirasi == 3:
                print("Girdim3")
                api = Siparis.api3
            ApiTuru = api.ApiTuru
            ApiTuruadi = ApiTuru.ApiYazilimAdi
            ApiBakiye = api.ApiBakiye
            gidenRefNumarasi = api.RefNumarasi
            api.RefNumarasi += 1
            api.save

            if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                paketler = VodafonePaketler.objects.filter(apiler=api)
                # Filtrelenmiş paketler listesinden, belirli bir kupür için ilgili bilgileri alın
                paket = paketler.filter(kupur=Siparis.PaketKupur).values('eslestirme_operator_adi',
                                                                                        'eslestirme_operator_tipi',
                                                                                        'eslestirme_kupur').first()
                # İstenen bilgileri değişkenlere atayın
                eslestirme_operator_adi = paket['eslestirme_operator_adi']
                eslestirme_operator_tipi = paket['eslestirme_operator_tipi']
                eslestirme_kupur = paket['eslestirme_kupur']
                print(str(eslestirme_operator_adi) + " " + str(eslestirme_operator_tipi) + " " + str(eslestirme_kupur))
            #                eslestirme_kupur = eslestirme_kupur.replace('.00','')

                url = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu={api.Kullaniciadi}&sifre={api.Sifre}&operator={eslestirme_operator_adi}&tip={eslestirme_operator_tipi}&kontor={eslestirme_kupur}&gsmno={Siparis.Numara}&tekilnumara={gidenRefNumarasi}"
            elif ApiTuruadi == "grafi":
                paketler = VodafonePaketler.objects.filter(apiler=api)
                # Filtrelenmiş paketler listesinden, belirli bir kupür için ilgili bilgileri alın
                paket = paketler.filter(kupur=Siparis.PaketKupur).values('eslestirme_kupur').first()
                # İstenen bilgileri değişkenlere atayın
                eslestirme_kupur = paket['eslestirme_kupur']
                url = f"https://{api.SiteAdresi}/api/islemal.asp?bayikodu={api.Kullanicikodu}&kadi={api.Kullaniciadi}&sifre={api.Sifre}&ope={eslestirme_kupur}&turu=5&miktar=0&telno={Siparis.Numara}&ref={gidenRefNumarasi}"

            response = requests.get(url)
            print(response.text)
            # TODO: işlem için Verilen Yeni Ref kayıt Yeri --- OK
            # TODO: işlem için Çekilen Tutarı kaydet olumlu olursa zaten düşmüş oluyorsun olumsuz olursa eklemen lazım.
            # TODO: işlem için Api ID si
            if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                response = response.text.split("|")
                GelenAciklama = Siparis.Aciklama
                if response[0] == "OK":
                    if response[1] == "1":
                        Siparis.SanalTutar = response[3]
                        Siparis.SanalRef = gidenRefNumarasi
                        Siparis.Durum = AnaPaketSonucBekler
                        Siparis.save()
                        api.ApiBakiye -= Decimal(response[3])
                        api.save()
                        Sonuc = response[2]

                    elif response[1] == "8" or response[1] == "3":
                        # Cevabı işleyin ve veritabanına kaydedin
                        # ...
                        Siparis.Durum = askida
                        Siparis.Aciklama = GelenAciklama + "\n Gelen Cevap = " + response[2]+" \n"
                        Siparis.save()
                        Sonuc = response[2]

                    else:
                        # Cevabı işleyin ve veritabanına kaydedin
                        # ...
                        Siparis.Durum = askida
                        Siparis.Aciklama = GelenAciklama + "\n Gelen Cevap = " + response[2]+" \n"
                        Siparis.save()
                        Sonuc = response[2]

                    return Sonuc

            elif ApiTuruadi == "grafi":
                response = response.text.split(" ")
                GelenAciklama = Siparis.Aciklama
                if response[0] == "OK":
                    Siparis.SanalRef = response[1]
                    Siparis.Durum = AnaPaketSonucBekler
                    Siparis.save()
                    api.save()
                    Sonuc = response
                else:
                    Siparis.Durum = askida
                    Siparis.Aciklama = GelenAciklama + "\n Gelen Cevap = " + str(response) + " \n"
                    Siparis.save()
                    Sonuc = response
                return Sonuc

        else:
            Sonuc = "Hiç Sipariş Yok"
            return Sonuc

def ApiZnetSiparisKaydet(request):
    # Gelen GET isteğindeki değerleri alın
    bayi_kodu = request.GET.get('bayi_kodu').strip().replace(' ','')
    sifre = request.GET.get('sifre').strip().replace(' ','')
    operatoru = request.GET.get('operator').strip().replace(' ','').lower()
    tip = request.GET.get('tip').strip().replace(' ','').lower()
    kontor = request.GET.get('kontor').strip().replace(' ','').replace('.00','').lower()
    gsmno = request.GET.get('gsmno').strip().replace(' ','').lower()
    tekilnumara = request.GET.get('tekilnumara').strip().replace(' ','').lower()

    # Gelen değerler doğruysa database'e kaydedins
    if bayi_kodu and sifre and operatoru and tip and kontor and gsmno and tekilnumara:
        # Siparisler sınıfından yeni bir nesne oluşturun
        try:
            user = User.objects.get(username=bayi_kodu)

            if user.check_password(sifre):
                order = Siparisler()
                try:
                    operator_model = AnaOperator.objects.get(AnaOperatorler=operatoru)
                except AnaOperator.DoesNotExist:
                    return HttpResponse("Operatör bilgisi hatalı.", status=400)  # 400 Bad Request HTTP response code
                try:
                    Tip_operator_model = AltOperator.objects.get(AltOperatorler=tip)
                except AltOperator.DoesNotExist:
                    return HttpResponse("Tip bilgisi hatalı.", status=400)

                #operator_model = AnaOperator.objects.get(AnaOperatorler=operatoru)
                #Tip_operator_model = AltOperator.objects.get(AltOperatorler=tip)

                order.Operator = operator_model
                order.OperatorTip = Tip_operator_model
                order.PaketKupur = kontor
                order.Numara = gsmno

                # Kontrol et, daha önce bu referans numarasıyla kaydedilen sipariş var mı?
                if Siparisler.objects.filter(GelenReferans=tekilnumara).exists():
                    sonuc = "Referans numarası daha önce kullanıldı."
                else:
                    order.GelenReferans = tekilnumara

                    # Kategori sınıfından ilgili kategoriyi bulun
                    kategori = Kategori.objects.filter(Operatoru=operator_model,
                                                       KategoriAltOperatoru=Tip_operator_model).first()

                    if kategori:
                        # Kontör listesinde ilgili kupur değerine sahip ürünü bulun
                        kontor_urunu = KontorList.objects.filter(Kupur=kontor, Kategorisi=kategori).first()
                        sorguGidicek = Durumlar.objects.get(durum_id=Durumlar.Sorguda)


                        #todo şimdilik kontör tutarı burada = 100
                        paket_tutari = Decimal('95.5')
                        Bayi = Bayi_Listesi.objects.get(user=user)
                        Onceki_Bakiye = Bayi.Bayi_Bakiyesi
                        onceki_Borc = Bayi.Borc



                        if kontor_urunu:
                            if Onceki_Bakiye - paket_tutari > 0:
                                Bayi.Bayi_Bakiyesi -= paket_tutari
                                Bayi.save()

                                SonrakiBakiye = Bayi.Bayi_Bakiyesi
                                sonraki_Borc = Bayi.Borc

                                # Ürün bulundu, api1, api2 ve api3 değerlerini siparişe ekle
                                order.user = user
                                order.api1 = kontor_urunu.api1
                                order.api2 = kontor_urunu.api2
                                order.api3 = kontor_urunu.api3
                                order.PaketAdi = kontor_urunu.Urun_adi
                                order.BayiAciklama = "İşleme Alındı."
                                order.Gonderim_Sirasi = 1
                                order.SanalKategori = kategori.pk
                                order.Durum = sorguGidicek  # Varsayılan durum
                                order.Aciklama = "Sipariş Kaydedildi.\n"

                                try:
                                    order.save()
                                    hareket = BakiyeHareketleri(user=user,
                                                                islem_tutari=paket_tutari,
                                                                onceki_bakiye=Onceki_Bakiye,
                                                                sonraki_bakiye=SonrakiBakiye,
                                                                onceki_Borc=onceki_Borc,
                                                                sonraki_Borc=sonraki_Borc,
                                                                aciklama=f"Kullanıcısı {user} Nolu Hatta {operatoru} {kontor} {paket_tutari} TL'lik bir paket satın aldı")
                                    hareket.save()

                                except Exception as e:
                                    print("Hata:", e)

                                sonuc = "OK|1|Talebiniz İşleme Alınmıştır.|44"
                            else:
                                sonuc = "OK|3|Yetersiz Bakiye.|0.00"

                        else:
                            sonuc = "OK|3|Tanımlı Paket Bulunamadı.|0.00"
                    else:
                        sonuc = "OK|3|KategoriBulunamadi.|0.00"

            else:
                return "Hatalı kullanıcı adı veya şifre"
        except (User.DoesNotExist, Siparisler.DoesNotExist):
            return "Kullanıcı veya sipariş bulunamadı"




    else:
        sonuc = "OK|3|EksikGelenBişilerVar.|0.00"

    return sonuc
def SonucKontrolGelen(request):
    bayi_kodu = request.GET.get('bayi_kodu').strip().replace(' ','')
    sifre = request.GET.get('sifre').strip().replace(' ','')
    tekilnumara = request.GET.get('tekilnumara').strip().replace(' ','')

    iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)
    Basarili = Durumlar.objects.get(durum_id=Durumlar.Basarili)

    try:
        user = User.objects.get(username=bayi_kodu)
        if user.check_password(sifre):
            siparis = Siparisler.objects.get(GelenReferans=tekilnumara)
            Sonuc_Durumu = siparis.Durum

            if Sonuc_Durumu == Basarili:
                aciklama = siparis.BayiAciklama
                tutar = siparis.SanalTutar
                return f"1:{aciklama}:{tutar}"
            elif Sonuc_Durumu == iptal:
                aciklama = siparis.BayiAciklama
                return f"3:{aciklama}:0"
            else:
                return "2:islemde:44"
        else:
            return "Hatalı kullanıcı adı veya şifre"
    except (User.DoesNotExist, Siparisler.DoesNotExist):
        return "Kullanıcı veya sipariş bulunamadı"


def PaketEkle(request):
    if request.method == 'POST':
        # Gelen POST isteğindeki değerleri alın
        Urun_adi = request.POST.get('Urun_adi')
        Kupur = request.POST.get('Kupur')
        GunSayisi = request.POST.get('GunSayisi')
        MaliyetFiyat = request.POST.get('MaliyetFiyat')
        HeryoneDK = request.POST.get('HeryoneDK')
        Sebekeici = request.POST.get('Sebekeici')
        internet = request.POST.get('internet')
        SMS = request.POST.get('SMS')
        YurtDisiDk = request.POST.get('YurtDisiDk')
        KategorisiCevir = request.POST.get('Kategorisi')
        api1Cevir = request.POST.get('api1')
        api2Cevir = request.POST.get('api2')
        zNetKupur = request.POST.get('zNetKupur')
        Kategorisi = Kategori.objects.get(pk=KategorisiCevir)
        api1 = Apiler.objects.get(pk=api1Cevir)
        api2 = Apiler.objects.get(pk=api2Cevir)

        # Gelen değerler doğruysa database'e kaydedin
        if HeryoneDK and Urun_adi and Kupur and GunSayisi and MaliyetFiyat :
            # Siparisler sınıfından yeni bir nesne oluşturun
            Kontor = KontorList()
            Kontor.HeryoneDK = HeryoneDK
            Kontor.Urun_adi = Urun_adi
            Kontor.Urun_Detay = Urun_adi
            Kontor.Kupur = Kupur
            Kontor.GunSayisi = GunSayisi
            Kontor.MaliyetFiyat = MaliyetFiyat
            Kontor.SatisFiyat = int(MaliyetFiyat) + 5
            Kontor.HeryoneDK = HeryoneDK
            Kontor.Sebekeici = Sebekeici
            Kontor.internet = internet
            Kontor.SMS = SMS
            Kontor.YurtDisiDk = YurtDisiDk
            Kontor.Aktifmi = True
            Kontor.Kategorisi = Kategorisi
            Kontor.api1 = api1
            Kontor.api2 = api2
            Kontor.zNetKupur = zNetKupur


            Kontor.save()

            Sonuc = "Sipariş başarıyla kaydedildi."

            return Sonuc
        else:
            Sonuc = "Eksik Bilgi"
            return Sonuc
    else:

        Sonuc = "Geçersiz istek Türü."
        return Sonuc


#TODO Sanırım bir tane Sorgudan gelen cevaplar için yer açmamız lazım siparişlerde ilk sorguya gittikten sonra gelen Altenatif listesi varsa onu kaydedip durumunu Mesela 45 yapıp
# #durumu 45 olanların içinde de alternatif var mı diye kontrol edip varsa o id yi yoksa zaten elimizde olan anayi işleme alıyoruz ve atmamız gereken id geliyor elimize Sorun şu ya iptal olursa ?

#TODO = Eğer bir alternatif çıkarsa siparişin durum ID sini farklı yapmak gerekebilir... Farklı bir Durum ID si yaparsak iptal gelirse  onun alternatif olduğunu biliriz ve bir sonrakine gitmek için çabalarız nasıl gideceğimi bilmiyorum
# sanırım listeden silerim o idleri ve tekrar listeyi for ' a sokarım  o zaman mantıklı olur olmayan tüm idleri listeden silmek lazım !
# Lakin şunua çok DIKKAT etmek lazım sildiğimizde for döngüsü elemanda atlama yapıyor mu ?  yapmıyor mu ? Burası önemli yapmıyorsa zaten çıkmayan tüm idleri anında sil
# Burada Ekstra Ultra Önemli bir not daha olsun bunları bizim alternatif ID Listemizden çekip silmek gerekebilir zannımca.

def SorguyaGonder():
    sorguda = Durumlar.objects.get(durum_id=Durumlar.Sorguda)
    sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
    aski = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
    orders = Siparisler.objects.filter(Durum=sorguda)
    if orders:
        for order in orders:
            print(order.Operator)
            print(order.Operator.AnaOperatorler)
            print(type(order.Operator.AnaOperatorler))
            print("uste")
            siteadi = "92.205.129.63:4244"
            # Apiler sınıfından şifre bilgilerini alın
            if order.Operator.AnaOperatorler == "vodafone":

                linki = f"http://{siteadi}/servis/tl_servis.php?bayi_kodu=VodafoneSorgudj&sifre=gerekyok&operator=vodafone&tip=vodafone&kontor=100444&gsmno={order.Numara}&tekilnumara=1{order.GelenReferans}"
            elif order.Operator == "turkcell":
                linki = f"http://{siteadi}/servis/tl_servis.php?bayi_kodu=TurkcellSorgudj&sifre=gerekyok&operator=turkcell&tip=turkcell&kontor=100443&gsmno={order.Numara}&tekilnumara=1{order.GelenReferans}"
            # Belirtilen URL'ye GET isteği gönderin

            url = linki
            #url = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&operator={order.Operator}&tip={order.operatorTip}&kontor={order.PaketKupur}&gsmno={order.numara}&tekilnumara={order.GelenReferans}"
            response = requests.get(url)
            print(response)
            response = response.text.split("|")
            if response[0] == "OK":
                if response[1] == "1":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    order.Durum = sorguCevap # Sorgu CEvap olarak güncellenecek
                    order.Aciklama = response[2]
                    order.SanalTutar = response[3]
                    order.SanalRef = f"1{order.GelenReferans}"
                    order.save()
                    Sonuc = response[2]
                    return Sonuc
                elif response[1] == "8":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    order.Durum = aski
                    order.Aciklama = response[2]
                    order.save()
                    Sonuc = response[2]
                    return Sonuc
                elif response[1] == "3":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    order.Durum = aski
                    order.Aciklama = response[2]
                    order.save()
                    Sonuc = response[2]
                    return Sonuc
                else:
                    order.Durum = 97
                    order.Aciklama = response[2]
                    order.save()
                    Sonuc = response[2]
                    return Sonuc
    else:
        Sonuc = "Hiç Sipariş Yok"
        return Sonuc

def SorguSonucKontrol():
    sorguda = Durumlar.objects.get(durum_id=Durumlar.Sorguda)
    sorgusutamam = Durumlar.objects.get(durum_id=Durumlar.SorguTamam)
    sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
    aski = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
    orders = Siparisler.objects.filter(Durum=sorguCevap)
    siteadi = "92.205.129.63:4244"
    if orders:
        for order in orders:
            # Apiler sınıfından şifre bilgilerini alın
            if order.Operator.AnaOperatorler == "vodafone":
                linki = f"http://{siteadi}/servis/tl_kontrol.php?bayi_kodu=VodafoneSorgudj&sifre=VodafoneSorgudj&tekilnumara={order.SanalRef}"
                #linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu=VodafoneSorgudj&sifre=gerekyok&operator=vodafone&tip=vodafone&kontor=100444&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"
            elif order.Operator == "turkcell":
                api = Apiler.objects.get(id=9)
                linki = f"http://{siteadi}/servis/tl_servis.php?bayi_kodu=TurkcellSorgudj&sifre=gerekyok&operator=turkcell&tip=turkcell&kontor=100443&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"





            url = linki
            #url = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&operator={order.Operator}&tip={order.operatorTip}&kontor={order.PaketKupur}&gsmno={order.numara}&tekilnumara={order.GelenReferans}"

         #   1: olumlu_islem:5.50
         #   2: islemde:5.50
         #   3: iptal_nedeni


            response = requests.get(url)
            print(response.text)
            response = response.text.split(":")
            if response[0] == "3":
                if response[1] == "1":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                   # order.Durum = sorguCevap # Sorgu CEvap olarak güncellenecek
                    order.Aciklama = response[2]
                    order.SanalTutar = response[3]

                    order.save()
                    api.ApiBakiye -= Decimal(response[3])
                    api.save()
                    Sonuc = response[2]
                    return Sonuc
                elif response[1] == "2":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    Sonuc = "Cevap Bekleniyor."
                    return Sonuc
                elif response[0] == "3":
                    print("Burada Olmam Lazım")

                    if response[1] == "TurkcellDegil":
                        #TODO iptal protokolü burada başlayacak Direk İptal edilecek!
                        order.Durum = sorgusutamam
                    else:
                        order.Durum = sorgusutamam
                     # order.Aciklama = GelenAciklama + response[1]
                        order.SorguPaketID = response[1].replace('|',',')

                    order.save()
                    Sonuc = response[1]
                    return Sonuc
                else:
                    order.Durum = 97
                    order.Aciklama = response[2]
                    order.save()
                    Sonuc = response[2]
                    return Sonuc
    else:
        Sonuc = "Hiç Sipariş Yok"
        return Sonuc











def AlternatifSonucKontrol():
    AlternatifVarmiBaska = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderim_Bekliyor)
    AlternatifVarmiBaska = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderimbekler)
    AnaPaketGoner = Durumlar.objects.get(durum_id=Durumlar.AnaPaketGoner)

    #Alternatif_islemde = Durumlar.objects.get(durum_id=Durumlar.Alternatif_islemde)
    #askida = Durumlar.objects.get(durum_id=Durumlar.askida)
    #Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)
    #sorgusutamam = Durumlar.objects.get(durum_id=Durumlar.SorguTamam)
    #sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
    #aski = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
    Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)
    Basarili = Durumlar.objects.get(durum_id=Durumlar.Basarili)
    iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)

    orders = YuklenecekSiparisler.objects.filter(YuklenecekPaketDurumu=Alternatif_Cevap_Bekliyor)
    if orders:
        for alternatifOrder in orders:
            ANA_Siparis = Siparisler.objects.get(id=alternatifOrder.ANAURUNID)

            if alternatifOrder.Gonderim_Sirasi == 1:
                print("Girdim1")
                api = alternatifOrder.Yuklenecek_api1
            if alternatifOrder.Gonderim_Sirasi == 2:
                print("Girdim2")
                api = alternatifOrder.Yuklenecek_api2
            if alternatifOrder.Gonderim_Sirasi == 3:
                print("Girdim3")
                api = alternatifOrder.Yuklenecek_api3

            linki = f"http://{api.SiteAdresi}/servis/tl_kontrol.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&tekilnumara={alternatifOrder.SanalRefIdesi}"
            print(linki)
            url = linki

            #   1: olumlu_islem:5.50
            #   2: islemde:5.50
            #   3: iptal_nedeni

            response = requests.get(url)
            print(response.text)
            response = response.text.split(":")
            if response[0] == "1":

                # Cevabı işleyin ve veritabanına kaydedin
                # ...
                # order.Durum = sorguCevap # Sorgu CEvap olarak güncellenecek
                # alternatifOrder.Aciklama = response[2]     #TODO buraya bayi aciklaması vs girilmesi lazım.
                # alternatifOrder.YuklenecekPaketFiyat = response[3]    #TODO Maliyete işlenmesi ve api fiyatında güncellenmesi lazım.
                alternatifOrder.YuklenecekPaketDurumu = Basarili
                print(response[1])
                if response[1] == "":
                    ANA_Siparis.BayiAciklama = "Basarili"
                else:
                    if response[1] =="Y%C3%BCklendi+-ONAYLANDI":
                        SonucCevabi = "Basarili"
                    else:
                        SonucCevabi = response[1]
                    ANA_Siparis.BayiAciklama = SonucCevabi
                    #alternatifOrder.Yukelenecek_Numara.BayiAciklama = response[1]
                alternatifOrder.Yukelenecek_Numara.SanalTutar = response[2]
                alternatifOrder.Yukelenecek_Numara.Durum = Basarili
                ANA_Siparis.SanalTutar = alternatifOrder.YuklenecekPaketFiyat
                ANA_Siparis.Durum = Basarili
                ANA_Siparis.SonucTarihi = timezone.now()
                alternatifOrder.save()
                ANA_Siparis.save()
                # api.ApiBakiye -= Decimal(response[3])
                # api.save()
                Sonuc = response[2]
                print("Durum güncellendi.")
                return Sonuc
            elif response[0] == "2":
                # Cevabı işleyin ve veritabanına kaydedin
                # ...
                Sonuc = "Henüz işlemde"
                return Sonuc
            elif response[0] == "3":
                api.ApiBakiye += Decimal(alternatifOrder.YuklenecekPaketFiyat)
                Sirasi = alternatifOrder.Gonderim_Sirasi + 1

                if Sirasi == 2:
                    print("Girdim2")
                    YeniApisi = alternatifOrder.Yuklenecek_api2

                if Sirasi == 3:
                    print("Girdim3")
                    YeniApisi = alternatifOrder.Yuklenecek_api2

                if not YeniApisi:
                    alternatifOrder.YuklenecekPaketDurumu = iptal

                    GelenAciklama = ANA_Siparis.Aciklama
                    ANA_Siparis.SonucTarihi = timezone.now()
                    ANA_Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " + api.Apiadi + " Apisinden " + \
                                           response[
                                               1] + "iptal olanApiSirasi:" + str(
                        alternatifOrder.Gonderim_Sirasi) + "\n"
                    alternatifOrder.save()
                    ANA_Siparis.save()

                    baskaAlternatifVarmi = YuklenecekSiparisler.objects.filter(YuklenecekPaketDurumu=AlternatifVarmiBaska).first()


                    if not  baskaAlternatifVarmi:
                        if ANA_Siparis.AnaPaketVar:
                            ANA_Siparis.Durum = AnaPaketGoner
                            ANA_Siparis.Aciklama = GelenAciklama + " Alternatif hiç bulunamadı AnaPaketAktifOlduğu için Gönderime alındı. \n"
                            ANA_Siparis.save()
                            AnaPaketGonder()
                        else:
                            ANA_Siparis.Durum = iptal
                            ANA_Siparis.SonucTarihi = timezone.now()
                            ANA_Siparis.Aciklama = GelenAciklama + " Alternatif hiç bulunamadı AnaPaketde olmadığı için iptal edildi. \n  Abone Bu Paketi Alamıyor Sanırım Yani Galiba. " + response[1]
                            ANA_Siparis.BayiAciklama = "Abone Bu Paketi Alamıyor Sanırım Yani Galiba. " + response[1]
                            ANA_Siparis.save()

                else:
                    print("Nasip")

                    alternatifOrder.YuklenecekPaketDurumu = AlternatifVarmiBaska
                    ANA_Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " + api.Apiadi + " Apisinden " + \
                                       response[1] + " iptal olanApiSirasi:" + str(alternatifOrder.Gonderim_Sirasi) + "\n"
                    alternatifOrder.Gonderim_Sirasi = Sirasi
                    alternatifOrder.save()
                    ANA_Siparis.save()
    else:
        Sonuc = "Hiç Sipariş Yok"
        return Sonuc






def AnaPaketSonucKontrol():
    iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)
    AnaPaket = Durumlar.objects.get(durum_id=Durumlar.AnaPaketGoner)
    sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
    aski = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
    AnaPaketSorgu = Durumlar.objects.get(durum_id=Durumlar.AnaPaketSonucBekler)
    Basarili = Durumlar.objects.get(durum_id=Durumlar.Basarili)

    SiparisTum = Siparisler.objects.filter(Durum=AnaPaketSorgu)
    if SiparisTum:
        for Siparis in SiparisTum:
            if Siparis:
                if Siparis.Gonderim_Sirasi == 1:
                    print("Girdim1")
                    api = Siparis.api1
                if Siparis.Gonderim_Sirasi == 2:
                    print("Girdim2")
                    api = Siparis.api2
                if Siparis.Gonderim_Sirasi == 3:
                    print("Girdim3")
                    api = Siparis.api3
            ApiTuru = api.ApiTuru
            ApiTuruadi = ApiTuru.ApiYazilimAdi
            if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                url = f"http://{api.SiteAdresi}/servis/tl_kontrol.php?bayi_kodu={api.Kullaniciadi}&sifre={api.Sifre}&tekilnumara={Siparis.SanalRef}"
            elif ApiTuruadi == "grafi":
                url = f"https://{api.SiteAdresi}/api/islemkontrol.asp?bayikodu={api.Kullaniciadi}&kadi={api.Kullaniciadi}&sifre={api.Sifre}&islem={Siparis.SanalRef}"
            response = requests.get(url)
            response.encoding = "ISO-8859-1"  # doğru kodlamayı burada belirtin
            print(response.text)
            if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                response = response.text.split(":")
            elif ApiTuruadi == "grafi":
                response = response.text.split(" ")
            GelenAciklama = Siparis.Aciklama

            if response[0] == "1" or response[0] == "OK":
                Siparis.Durum = Basarili
                Siparis.SonucTarihi = timezone.now()
                if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                    if response[1] == "":
                        print("NasipGrimesi lazım")
                        Siparis.BayiAciklama = "Basarili"
                    else:
                        Siparis.BayiAciklama = response[1]
                elif ApiTuruadi== "grafi":
                    Siparis.BayiAciklama = "Basarili"
                    api.ApiBakiye -= Decimal(response[1])
                    Siparis.SanalTutar = response[1]



                Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " +api.Apiadi+" Apisinden "+ response[1] + "\n"
                Siparis.save()
                Sonuc = "Basarili İslem"
                return Sonuc
            elif response[0] == "2" or response[0] == "99":
                Sonuc = "Henüz işlemde"
                return Sonuc
            elif response[0] == "3" or response[0] == "98":
                if ApiTuruadi == 'Znet' or ApiTuruadi == "Gencan":
                    api.ApiBakiye += Decimal(Siparis.SanalTutar)
                Sirasi = Siparis.Gonderim_Sirasi +1
                if Sirasi == 2:
                    print("Girdim2")
                    YeniApisi = Siparis.api2

                if Sirasi == 3:
                    print("Girdim3")
                    YeniApisi = Siparis.api3

                if not YeniApisi:
                    Siparis.Durum = iptal
                    Siparis.SonucTarihi = timezone.now()
                    Siparis.BayiAciklama = "iptal"
                    Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: "+api.Apiadi+" Apisinden " + response[
                        1] + "iptal olanApiSirasi:" + str(Siparis.Gonderim_Sirasi) + " Başka Api olmadığı için iptal edildi.\n"
                    Siparis.save()

                    paket_tutari = Decimal('95.5')
                    user = User.objects.get(username=Siparis.user)
                    Bayi = Bayi_Listesi.objects.get(user=user)
                    Onceki_Bakiye = Bayi.Bayi_Bakiyesi
                    onceki_Borc = Bayi.Borc
                    Bayi.Bayi_Bakiyesi += paket_tutari
                    Bayi.save()
                    SonrakiBakiye = Bayi.Bayi_Bakiyesi
                    sonraki_Borc = Bayi.Borc

                    hareket = BakiyeHareketleri(user=user,
                                                islem_tutari=paket_tutari,
                                                onceki_bakiye=Onceki_Bakiye,
                                                sonraki_bakiye=SonrakiBakiye,
                                                onceki_Borc=onceki_Borc,
                                                sonraki_Borc=sonraki_Borc,
                                                aciklama=f"{Siparis.Numara} Nolu Hatta {paket_tutari} TL'lik bir paket yüklenemedi Bakiyesi iade edildii.")
                    hareket.save()
                else:
                    Siparis.Durum = AnaPaket
                    Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: "+api.Apiadi+" Apisinden " + response[1] +" iptal olanApiSirasi:"+str(Siparis.Gonderim_Sirasi)+ "\n"
                    Siparis.Gonderim_Sirasi = Sirasi
                    Siparis.save()
                    AnaPaketGonder()

    else:
        Sonuc = "Hiç Sipariş Yok"
        return Sonuc







def AlternatifKontrol(request):

    #TODO = buradaki soguda kısmı değişicek sorgu Sonucu olarak önce tanımlaman lazım tabiki
    sorguda = Durumlar.objects.get(durum_id=Durumlar.Sorguda)
    iptalEdildi = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)
    sorgusutamam = Durumlar.objects.get(durum_id=Durumlar.SorguTamam)
    AnaPaketGonderDurumu = Durumlar.objects.get(durum_id=Durumlar.AnaPaketGoner)



    AltPaketID = Durumlar.objects.get(durum_id=Durumlar.AltKontrol)
    siparisler = Siparisler.objects.filter(Durum=sorgusutamam)

    # 2- Siparişin Kategorisi ve PaketKupur değerlerine ulaşıyoruz.
    for siparis in siparisler:
        siparis_kupur = siparis.PaketKupur
        siparis_kategorisi = siparis.SanalKategori

        # 3 - Kategorideki paketi arattıktan sonra çıkan Paketin "KontorList" Classındaki "alternatif_urunler"deki tüm ürünleri alıyoruz.
        kategorideki_paket = KontorList.objects.get(Kupur=siparis_kupur, Kategorisi=siparis_kategorisi)

        kategorideki_paket_alternatifleri = AlternativeProduct.objects.filter(main_product=kategorideki_paket)


        # 4 - Aldığımız Tüm alternatif_urunlerdeki ID ileri sırasıyla Siparişlerdeki "SorguPaketID" ile karşılaştırıyoruz.
        # TODO Eğer Sadece Text Gelen bir aciklama gelirse try excepte giricek ve sonuca bakacak
        try:
            PaketSorguListesi = []
            for siparis in siparisler:
                paket_idler = siparis.SorguPaketID.split(",")
                for paket_id in paket_idler:
                    PaketSorguListesi.append(int(paket_id))
            cikan_idler = []
            for alternative in kategorideki_paket_alternatifleri:
                if alternative.product_id in PaketSorguListesi:
                    cikan_idler.append(alternative.product_id)
        except:

            if siparis.SorguPaketID == "VodafoneDegilKi,GNC001" or  siparis.SorguPaketID == "TurkcellDegilKi,GNC001":
                siparis.Durum = iptalEdildi
                siparis.SonucTarihi = timezone.now()
                siparis.BayiAciklama = siparis.SorguPaketID
                #siparisler.BayiAciklama = siparis.SorguPaketID
                siparis.save()
                paket_tutari = Decimal('95.5')
                user = User.objects.get(username=siparis.user)
                Bayi = Bayi_Listesi.objects.get(user=user)
                Onceki_Bakiye = Bayi.Bayi_Bakiyesi
                onceki_Borc = Bayi.Borc
                Bayi.Bayi_Bakiyesi += paket_tutari
                Bayi.save()
                SonrakiBakiye = Bayi.Bayi_Bakiyesi
                sonraki_Borc = Bayi.Borc

                hareket = BakiyeHareketleri(user=user,
                                            islem_tutari=paket_tutari,
                                            onceki_bakiye=Onceki_Bakiye,
                                            sonraki_bakiye=SonrakiBakiye,
                                            onceki_Borc=onceki_Borc,
                                            sonraki_Borc=sonraki_Borc,
                                            aciklama=f"{siparis.Numara} Nolu Hatta {paket_tutari} TL'lik bir paket yüklenemedi Bakiyesi iade edildii.")
                hareket.save()
                return "Oto İPTAL edildi"


        # AnaPaketVar mi Kontrollü

        #vergiList=['8703','7353','7354','7355']


        if len(cikan_idler) == 0:
            if '8703' in PaketSorguListesi:
                print("En az 18TL lik vergi Borcu var.")
                vergiTutari = "En az 18TL yüklemesi gerekiyor vergi borcu var."
            if '7353' in PaketSorguListesi:
                print("En az 36TL lik vergi Borcu var.")
                vergiTutari = "En az 36TL yüklemesi gerekiyor vergi borcu var."
            if '7354' in PaketSorguListesi:
                print("En az 54TL lik vergi Borcu var.")
                vergiTutari = "En az 54TL yüklemesi gerekiyor vergi borcu var."
            if '7355' in PaketSorguListesi:
                print("En az 72TL lik vergi Borcu var.")
                vergiTutari = "En az 72TL yüklemesi gerekiyor vergi borcu var."
            siparis.Durum = iptalEdildi
            siparis.SonucTarihi = timezone.now()
            siparis.BayiAciklama = vergiTutari + " Yükleme yaptıkran 5 DK sonra paketi gönderebilirsiniz."
            # siparisler.BayiAciklama = siparis.SorguPaketID
            siparis.save()
            paket_tutari = Decimal('95.5')
            user = User.objects.get(username=siparis.user)
            Bayi = Bayi_Listesi.objects.get(user=user)
            Onceki_Bakiye = Bayi.Bayi_Bakiyesi
            onceki_Borc = Bayi.Borc
            Bayi.Bayi_Bakiyesi += paket_tutari
            Bayi.save()
            SonrakiBakiye = Bayi.Bayi_Bakiyesi
            sonraki_Borc = Bayi.Borc

            hareket = BakiyeHareketleri(user=user,
                                        islem_tutari=paket_tutari,
                                        onceki_bakiye=Onceki_Bakiye,
                                        sonraki_bakiye=SonrakiBakiye,
                                        onceki_Borc=onceki_Borc,
                                        sonraki_Borc=sonraki_Borc,
                                        aciklama=f"{siparis.Numara} Nolu Hatta {paket_tutari} TL'lik bir paket yüklenemedi Bakiyesi iade edildii.")
            hareket.save()
            return "Oto İPTAL edildi"






        if siparis_kupur in PaketSorguListesi:
            print("Aranan değer listede var.")
            siparis.AnaPaketVar = True
        else:
            print("Aranan değer listede yok.")
            siparis.AnaPaketVar = False

        # 5- en son o listeyi print ile yazdırıyoruz.
        if len(cikan_idler) > 0:
            GelenAciklama = siparis.Aciklama
            siparis.Durum = AltPaketID

            GelenAciklama = GelenAciklama + "\n PaketSorgudan Gelen ID = " + siparis.SorguPaketID + "\n"
            siparis.SorguPaketID = ""
            str_cikan_idler = ",".join([str(id) for id in cikan_idler])
            siparis.SorguPaketID = str_cikan_idler

            GelenAciklama = GelenAciklama + "Bulunan Alternatif ID = " + str_cikan_idler + "\n"
            siparis.Aciklama = GelenAciklama
            siparis.save()
#todo burada anapaket var mı yok mu kontrol etmen ona göre iptal etmen yada yüklemeye gödnermen lazım.
        # Todo Olmadı bir testini yap ona göre bak.
        else:
            if siparis.AnaPaketVar:
                GelenAciklama = siparis.Aciklama
                siparis.Durum = AnaPaketGonderDurumu

                GelenAciklama = GelenAciklama + "\n PaketSorgudan Gelen ID = " + siparis.SorguPaketID + "\n"
                siparis.SorguPaketID = ""
                GelenAciklama = GelenAciklama + "Hiç Eşleşen Alternatif Bulunamadi. Orjinal Paket Yüklemeye Gönderiliyor.\n"
                siparis.Aciklama = GelenAciklama
                siparis.save()
                AnaPaketGonder()
            else:
                siparis.Durum = iptalEdildi
                siparis.SonucTarihi = timezone.now()
                siparis.BayiAciklama = "Vergi Borcu Olabilir."
                # siparisler.BayiAciklama = siparis.SorguPaketID
                siparis.save()
                paket_tutari = Decimal('95.5')
                user = User.objects.get(username=siparis.user)
                Bayi = Bayi_Listesi.objects.get(user=user)
                Onceki_Bakiye = Bayi.Bayi_Bakiyesi
                onceki_Borc = Bayi.Borc
                Bayi.Bayi_Bakiyesi += paket_tutari
                Bayi.save()
                SonrakiBakiye = Bayi.Bayi_Bakiyesi
                sonraki_Borc = Bayi.Borc

                hareket = BakiyeHareketleri(user=user,
                                            islem_tutari=paket_tutari,
                                            onceki_bakiye=Onceki_Bakiye,
                                            sonraki_bakiye=SonrakiBakiye,
                                            onceki_Borc=onceki_Borc,
                                            sonraki_Borc=sonraki_Borc,
                                            aciklama=f"{siparis.Numara} Nolu Hatta {paket_tutari} TL'lik bir paket & Ana Paket bulunamadı Bakiyesi iade edildii.")
                hareket.save()





def YuklenecekPaketler(request):
    #TODO aşası Tamam HAzır kod sakın bozma
    # Durumu 31 olan siparişleri çekiyoruz
    #siparisler = Siparisler.objects.filter(Durum=31)
    altkontrol31 = Durumlar.objects.get(durum_id=Durumlar.AltKontrol)
    alternatifdeneyen10 = Durumlar.objects.get(durum_id=Durumlar.ALTERNATIF_DENEYEN)
    Alternatif_Gonder = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderimbekler)
    Alternatif_Gonderim_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderim_Bekliyor)
    siparisler = Siparisler.objects.filter(Durum=altkontrol31)
    print("Nasip0001")
    for siparis in siparisler:
        # Siparişin sanal kategorisini alıyoruz
        kategori = siparis.SanalKategori
        print(kategori)
        # Siparişin sorgu paket ID'lerini alıyoruz
        paketler = siparis.SorguPaketID.split(',')
        print(paketler)
        YuklenecekPaketListesi = []
        for paket in paketler:
            # YuklenecekPaketListesi değişkenine paketleri ekliyoruz
            YuklenecekPaketListesi.append(paket)

        print(YuklenecekPaketListesi)
        print("YuklenecekPaketListesiYukarıda.")
        # YuklenecekPaketListesi içerisindeki her bir paketin kategorisindeki paketi buluyoruz
        DonguKontrol = 0
        for paket in YuklenecekPaketListesi:
            print(paket+"Apisinden"+kategori)
            kategorideki_paket = KontorList.objects.get(Kupur=paket, Kategorisi=kategori)
            print(kategorideki_paket)
            PaketinAdi = kategorideki_paket.Urun_adi
            PaketinID = paket

            Yuklene_api1 = kategorideki_paket.api1
            Yuklene_api2 = kategorideki_paket.api2
            Yuklene_api3 = kategorideki_paket.api3
            DonguKontrol += 1


            if DonguKontrol == 1:
                yuklenecek_siparis = YuklenecekSiparisler.objects.create(
                    YuklenecekPaketAdi=PaketinAdi,
                    YuklenecekPaketID=PaketinID,
                    YuklenecekPaketDurumu=Alternatif_Gonder,
                    Yuklenecek_api1=Yuklene_api1,
                    Yuklenecek_api2=Yuklene_api2,
                    Yuklenecek_api3=Yuklene_api3,
                    Gonderim_Sirasi = 1,
                    Yukelenecek_Numara=siparis , # ilgili Siparisler nesnesini ekleyin
                    ANAURUNID=siparis.id  # ilgili Siparisler nesnesini ekleyin

                )
            else:
                yuklenecek_siparis = YuklenecekSiparisler.objects.create(
                    YuklenecekPaketAdi=PaketinAdi,
                    YuklenecekPaketID=PaketinID,
                    YuklenecekPaketDurumu=Alternatif_Gonderim_Bekliyor,
                    Yuklenecek_api1=Yuklene_api1,
                    Yuklenecek_api2=Yuklene_api2,
                    Yuklenecek_api3=Yuklene_api3,
                    Gonderim_Sirasi = 1,
                    Yukelenecek_Numara=siparis , # ilgili Siparisler nesnesini ekleyin
                    ANAURUNID=siparis.id  # ilgili Siparisler nesnesini ekleyin
                )
        siparis.Durum = alternatifdeneyen10
        siparis.save()
        # YuklenecekPaketListesi'ni sıfırlıyoruz
        YuklenecekPaketListesi.clear()

    # Başarılı bir şekilde tamamlandığına dair bir mesaj döndürüyoruz
    return HttpResponse('Yuklenecek paketler basariyla kaydedildi.')


def AlternatifYuklemeyeHazirla(request):
    # Sipariş durumu 10 olan tüm siparişleri çek
    alternatifdeneyen10 = Durumlar.objects.get(durum_id=Durumlar.ALTERNATIF_DENEYEN)

    siparisler = Siparisler.objects.filter(Durum=alternatifdeneyen10)

    # Her siparişin yüklenecek siparişlerini çek
    yuklenecek_siparisler = []
    for siparis in siparisler:
        siparis_yuklenecekleri = siparis.yuklenecek_siparisler.all()

        # Her yüklenecek siparişin özelliklerini yazdır
        for yuklenecek_siparis in siparis_yuklenecekleri:
            print(f"YuklenecekPaketID: {yuklenecek_siparis.YuklenecekPaketID}")
            print(f"YuklenecekPaketDurumu: {yuklenecek_siparis.YuklenecekPaketDurumu}")
            print(f"Yuklenecek_api1: {yuklenecek_siparis.Yuklenecek_api1}")

            # Yuklenecek siparişleri listeye ekle
            yuklenecek_siparisler.append(yuklenecek_siparis)

    # Başarılı bir şekilde tamamlandığına dair bir mesaj döndürüyoruz
    return HttpResponse('Sipariş durumu 10 olanların yüklenecek siparişleri başarıyla listelendi.')
# todo üstekine bir bak hele ne poka yarıyormuş



def AlternatifYuklemeGonder():
    Alternatif_Gonderimbekler = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Gonderimbekler)
    Alternatif_islemde = Durumlar.objects.get(durum_id=Durumlar.Alternatif_islemde)
    askida = Durumlar.objects.get(durum_id=Durumlar.askida)
    Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)


    alternatifOrders = YuklenecekSiparisler.objects.filter(YuklenecekPaketDurumu=Alternatif_Gonderimbekler)
    if alternatifOrders:
        for alternatifOrder in alternatifOrders:
            #api = order.Yuklenecek_api1
            #print(api)

            if alternatifOrder.Gonderim_Sirasi == 1:
                print("Girdim1")
                api = alternatifOrder.Yuklenecek_api1
            if alternatifOrder.Gonderim_Sirasi == 2:
                print("Girdim2")
                api = alternatifOrder.Yuklenecek_api2
            if alternatifOrder.Gonderim_Sirasi == 3:
                print("Girdim3")
                api = alternatifOrder.Yuklenecek_api3

            ApiTuru = api.ApiTuru
            ApiTuruadi = ApiTuru.ApiYazilimAdi
            ApiBakiye = api.ApiBakiye
            gidenRefNumarasi = api.RefNumarasi
            api.RefNumarasi += 1
            api.save
            print(ApiTuru)
            print(ApiTuruadi)
            print(ApiBakiye)
            print(gidenRefNumarasi)

            if ApiTuruadi == 'Znet' or ApiTuruadi == 'Gencan':
                paketler = VodafonePaketler.objects.filter(apiler=api)

                # Filtrelenmiş paketler listesinden, belirli bir kupür için ilgili bilgileri alın
                paket = paketler.filter(kupur=alternatifOrder.YuklenecekPaketID).values('eslestirme_operator_adi', 'eslestirme_operator_tipi',
                                                            'eslestirme_kupur').first()
                #TODO buraya Paket eşleştirmesi yok hatası ver 930' da patlıyor.
                # İstenen bilgileri değişkenlere atayın
                eslestirme_operator_adi = paket['eslestirme_operator_adi']
                eslestirme_operator_tipi = paket['eslestirme_operator_tipi']
                eslestirme_kupur = paket['eslestirme_kupur']
                print(str(eslestirme_operator_adi)+" "+str(eslestirme_operator_tipi)+" "+str(eslestirme_kupur))
#                eslestirme_kupur = eslestirme_kupur.replace('.00','')


            linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&operator={eslestirme_operator_adi}&tip={eslestirme_operator_tipi}&kontor={eslestirme_kupur}&gsmno={alternatifOrder.Yukelenecek_Numara.Numara}&tekilnumara={gidenRefNumarasi}"

            url = linki
            print(linki)
            response = requests.get(url)
            print(response.text)
            # TODO: işlem için Verilen Yeni Ref kayıt Yeri --- OK
            # TODO: işlem için Çekilen Tutarı kaydet olumlu olursa zaten düşmüş oluyorsun olumsuz olursa eklemen lazım.
            # TODO: işlem için Api ID si
            response = response.text.split("|")
            if response[0] == "OK":
                if response[1] == "1":
                    alternatifOrder.YuklenecekPaketDurumu = Alternatif_islemde #Devamı Lazım.
                    #alternatifOrder.Aciklama = response[2]
                    alternatifOrder.YuklenecekPaketFiyat = response[3]
                    alternatifOrder.SanalRefIdesi = gidenRefNumarasi
                    alternatifOrder.YuklenecekPaketDurumu = Alternatif_Cevap_Bekliyor
                    alternatifOrder.save()
                    api.ApiBakiye -= Decimal(response[3])
                    api.save()
                    Sonuc = response[2]
                    return Sonuc
                elif response[1] == "8":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    alternatifOrder.YuklenecekPaketDurumu = askida
                   # alternatifOrder.Aciklama = response[2]
                    alternatifOrder.save()
                    Sonuc = response[2]
                    return Sonuc
                elif response[1] == "3":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    alternatifOrder.YuklenecekPaketDurumu = askida
                   # alternatifOrder.Aciklama = response[2]
                    alternatifOrder.save()
                    Sonuc = response[2]
                    return Sonuc
                else:
                    alternatifOrder.YuklenecekPaketDurumu = 97
                   # alternatifOrder.Aciklama = response[2]
                    alternatifOrder.save()
                    Sonuc = response[2]
                    return Sonuc
    else:
        Sonuc = "Hiç Sipariş Yok"
        return Sonuc



def VodafonePaketleriCek(request):
    eklenen_paketler=[]
    silinen_paketler=[]
    response = requests.post('http://92.205.129.63:4244/Sorgu.php', data={
        'python': 'PaketCekVodafoneAll'
    })
    if response.status_code == 200:
        data = response.content.decode('utf-8')
        paketler = data.split('|')
        for paket in paketler:
            if not paket.strip():
                continue
            bilgiler = paket.split('/')
            paketID = float(bilgiler[0])
            Paket = bilgiler[1]
            paketDK = float(bilgiler[2])
            paketGB = float(bilgiler[3]) * 1000  # str(int(bilgiler[3]) * 1000)
            paketSMS = float(bilgiler[4])
            paketFiyat = Decimal(bilgiler[5])
            paketDay = float(bilgiler[6])
            znetFix = Decimal(bilgiler[7]) if bilgiler[7].strip() and bilgiler[7] != 'Bulamadım.' else Decimal('0.00')
            if bilgiler[8] == "evet":
                alternatif_bilgisi = True
            else:
                alternatif_bilgisi = False
            alternatifyapilmasin = alternatif_bilgisi
            PaketNames = bilgiler[9]
            KategorisiGelen = Kategori.objects.get(pk=3)
            api1 = Apiler.objects.get(pk=3)
            api2 = Apiler.objects.get(pk=2)
            api3 = Apiler.objects.get(pk=1)
            SatisFiyat = paketFiyat + Decimal('5.00')
            GelenPaket = KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID)
            if GelenPaket.exists():
                #print("Paket ---Update girdim")
                # güncelleme işlemi yapılır
                PaketiGuncelle = GelenPaket.first()
                PaketiGuncelle.Urun_adi = PaketNames
                PaketiGuncelle.Urun_Detay = Paket
                PaketiGuncelle.Kupur = paketID
                PaketiGuncelle.zNetKupur = znetFix
                PaketiGuncelle.GunSayisi = paketDay
                PaketiGuncelle.MaliyetFiyat = paketFiyat
                PaketiGuncelle.SatisFiyat = SatisFiyat
                PaketiGuncelle.HeryoneDK = paketDK
                PaketiGuncelle.Sebekeici = Decimal('0.00')
                PaketiGuncelle.internet = paketGB
                PaketiGuncelle.SMS = paketSMS
                PaketiGuncelle.api3 = api3
                PaketiGuncelle.AlternatifYapilmasin = alternatifyapilmasin

                PaketiGuncelle.save()

            else:
                eklenen_paketler.append(str(paketID))
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = KontorList(
                    Kupur=paketID,
                    Urun_adi=PaketNames,
                    Urun_Detay=Paket,
                    GunSayisi=paketDay,
                    MaliyetFiyat=paketFiyat,
                    SatisFiyat=Decimal(int(paketFiyat) + 5),
                    HeryoneDK=paketDK,
                    Sebekeici=Decimal('0.00'),
                    internet=Decimal(paketGB),
                    SMS=paketSMS,
                    YurtDisiDk=Decimal('0.00'),
                    Aktifmi=True,
                    Kategorisi=KategorisiGelen,
                    api1=api1,
                    api2=api2,
                    zNetKupur=znetFix,
                    AlternatifYapilmasin = alternatifyapilmasin
                )
                paketEkle.save()

    # Vodafoneye ait Mevcut paketleri veritabanından getir
    KategorisiGelen = Kategori.objects.get(pk=3)
    mevcut_paketler = KontorList.objects.filter(Kategorisi=KategorisiGelen)

    # Olmayah Paketleri Siler
    # Gelen listedeki her bir paketi döngü ile kontrol et
    kontrol = []

    for paketi in paketler:
        if not paketi.strip():
            continue
        bilgiler = paketi.split('/')
        paketID = float(bilgiler[0])
        kontrol.append(paketID)

    mevcut_paketler = KontorList.objects.filter(Kategorisi=KategorisiGelen)
    for paket in mevcut_paketler:
        paketID = paket.Kupur
        if paketID not in kontrol:
            silinen_paketler.append(str(paketID))
            KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID).delete()

    return HttpResponse(f'İşlem tamamlandı. Eklenen paketler: {eklenen_paketler}, silinen paketler: {silinen_paketler}')


def TurkcellPaketleriCek(request):
    eklenen_paketler=[]
    silinen_paketler=[]
    response = requests.post('http://92.205.129.63:4244/Sorgu.php', data={
        'python': 'PaketCekTurkcellAll'
    })
    if response.status_code == 200:
        data = response.content.decode('utf-8')
        paketler = data.split('|')
        for paket in paketler:
            if not paket.strip():
                continue
            bilgiler = paket.split('/')
            paketID = float(bilgiler[0])
            Paket = bilgiler[1]
            paketDK = float(bilgiler[2])
            paketGB = float(bilgiler[3])*1000  #    str(int(bilgiler[3]) * 1000)
            paketSMS = float(bilgiler[4])
            paketFiyat = Decimal(bilgiler[5])
            paketDay = float(bilgiler[6])
            znetFix = Decimal(bilgiler[7]) if bilgiler[7].strip() and bilgiler[7] != 'Bulamadım.' else Decimal('0.00')
            if bilgiler[8] == "evet":
                alternatif_bilgisi = True
            else:
                alternatif_bilgisi = False
            alternatifyapilmasin = alternatif_bilgisi
            PaketNames = bilgiler[9]

            KategorisiGelen = Kategori.objects.get(pk=1)
            api1 = Apiler.objects.get(pk=3)
            api2 = Apiler.objects.get(pk=2)
            api3 = Apiler.objects.get(pk=1)
            SatisFiyat = paketFiyat + Decimal('5.00')
            GelenPaket = KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID)
            if GelenPaket.exists():
                #print("Paket ---Update girdim")
                # güncelleme işlemi yapılır
                PaketiGuncelle = GelenPaket.first()
                PaketiGuncelle.Urun_adi = PaketNames
                PaketiGuncelle.Urun_Detay = Paket
                PaketiGuncelle.Kupur = paketID
                PaketiGuncelle.zNetKupur = znetFix
                PaketiGuncelle.GunSayisi = paketDay
                PaketiGuncelle.MaliyetFiyat = paketFiyat
                PaketiGuncelle.SatisFiyat = SatisFiyat
                PaketiGuncelle.HeryoneDK = paketDK
                PaketiGuncelle.Sebekeici = Decimal('0.00')
                PaketiGuncelle.internet = paketGB
                PaketiGuncelle.SMS = paketSMS
                PaketiGuncelle.api3 = api3
                PaketiGuncelle.AlternatifYapilmasin = alternatifyapilmasin

                PaketiGuncelle.save()

            else:
                eklenen_paketler.append(str(paketID))
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = KontorList(
                    Kupur=paketID,
                    Urun_adi=PaketNames,
                    Urun_Detay=Paket,
                    GunSayisi=paketDay,
                    MaliyetFiyat=paketFiyat,
                    SatisFiyat=Decimal(int(paketFiyat) + 5),
                    HeryoneDK=paketDK,
                    Sebekeici=Decimal('0.00'),
                    internet=Decimal(paketGB),
                    SMS=paketSMS,
                    YurtDisiDk=Decimal('0.00'),
                    Aktifmi=True,
                    Kategorisi=KategorisiGelen,
                    api1=api1,
                    api2=api2,
                    zNetKupur=znetFix,
                    AlternatifYapilmasin = alternatifyapilmasin
                )
                paketEkle.save()

    # Vodafoneye ait Mevcut paketleri veritabanından getir
    KategorisiGelen = Kategori.objects.get(pk=1)
    mevcut_paketler = KontorList.objects.filter(Kategorisi=KategorisiGelen)

    # Olmayah Paketleri Siler
    # Gelen listedeki her bir paketi döngü ile kontrol et
    kontrol = []

    for paketi in paketler:
        if not paketi.strip():
            continue
        bilgiler = paketi.split('/')
        paketID = float(bilgiler[0])
        kontrol.append(paketID)

    mevcut_paketler = KontorList.objects.filter(Kategorisi=KategorisiGelen)
    for paket in mevcut_paketler:
        paketID = paket.Kupur
        if paketID not in kontrol:
            silinen_paketler.append(str(paketID))
            KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID).delete()

    return HttpResponse(f'İşlem tamamlandı. Eklenen paketler: {eklenen_paketler}, silinen paketler: {silinen_paketler}')