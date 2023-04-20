from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,AnaOperator,AltOperator,KontorList,Kategori,AlternativeProduct,YuklenecekSiparisler,Durumlar,VodafonePaketler
import requests
from decimal import Decimal

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

            linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&operator={eslestirme_operator_adi}&tip={eslestirme_operator_tipi}&kontor={eslestirme_kupur}&gsmno={Siparis.Numara}&tekilnumara={gidenRefNumarasi}"
            url = linki
            print(linki)
            response = requests.get(url)
            print(response.text)
            # TODO: işlem için Verilen Yeni Ref kayıt Yeri --- OK
            # TODO: işlem için Çekilen Tutarı kaydet olumlu olursa zaten düşmüş oluyorsun olumsuz olursa eklemen lazım.
            # TODO: işlem için Api ID si
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
                    return Sonuc
                elif response[1] == "8" or response[1] == "3":
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    Siparis.Durum = askida
                    Siparis.Aciklama = GelenAciklama + "\n Gelen Cevap = " + response[2]+" \n"
                    Siparis.save()
                    Sonuc = response[2]
                    return Sonuc
                else:
                    # Cevabı işleyin ve veritabanına kaydedin
                    # ...
                    Siparis.Durum = askida
                    Siparis.Aciklama = GelenAciklama + "\n Gelen Cevap = " + response[2]+" \n"
                    Siparis.save()
                    Sonuc = response[2]
                    return Sonuc
        else:
            Sonuc = "Hiç Sipariş Yok"
            return Sonuc

def ApiZnetSiparisKaydet(request):
    # Gelen GET isteğindeki değerleri alın
    bayi_kodu = request.GET.get('bayi_kodu')
    sifre = request.GET.get('sifre')
    operatoru = request.GET.get('operator')
    tip = request.GET.get('tip')
    kontor = request.GET.get('kontor')
    gsmno = request.GET.get('gsmno')
    tekilnumara = request.GET.get('tekilnumara')

    # Gelen değerler doğruysa database'e kaydedin
    if bayi_kodu and sifre and operatoru and tip and kontor and gsmno and tekilnumara:
        # Siparisler sınıfından yeni bir nesne oluşturun
        order = Siparisler()

        operator_model = AnaOperator.objects.get(AnaOperatorler=operatoru)
        Tip_operator_model = AltOperator.objects.get(AltOperatorler=tip)

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
            kategori = Kategori.objects.filter(Operatoru=operator_model, KategoriAltOperatoru=Tip_operator_model).first()

            if kategori:
                # Kontör listesinde ilgili kupur değerine sahip ürünü bulun
                kontor_urunu = KontorList.objects.filter(Kupur=kontor, Kategorisi=kategori).first()
                sorguGidicek = Durumlar.objects.get(durum_id=Durumlar.Sorguda)

                if kontor_urunu:
                    # Ürün bulundu, api1, api2 ve api3 değerlerini siparişe ekle
                    order.api1 = kontor_urunu.api1
                    order.api2 = kontor_urunu.api2
                    order.api3 = kontor_urunu.api3
                    order.PaketAdi = kontor_urunu.Urun_adi
                    order.BayiAciklama = "İşleme Alındı."
                    order.Gonderim_Sirasi = 1
                    order.SanalKategori = kategori.pk
                    order.Durum = sorguGidicek # Varsayılan durum
                    order.Aciklama = "Sipariş Kaydedildi.\n"
                    order.save()

                    sonuc = "Sipariş başarıyla kaydedildi."
                else:
                    sonuc = "Tanımlı Paket Bulunamadı"
            else:
                sonuc = "Kategori Bulunamadı"

    else:
        sonuc = "Hatalı"

    return sonuc
########
########def ApiZnetSiparisKaydet(request):
########    # Gelen GET isteğindeki değerleri alın
########    bayi_kodu = request.GET.get('bayi_kodu')
########    sifre = request.GET.get('sifre')
########    operatoru = request.GET.get('operator')
########    tip = request.GET.get('tip')
########    kontor = request.GET.get('kontor')
########    gsmno = request.GET.get('gsmno')
########    tekilnumara = request.GET.get('tekilnumara')
########
########    # Gelen değerler doğruysa database'e kaydedin
########    if bayi_kodu and sifre and operatoru and tip and kontor and gsmno and tekilnumara:
########        # Siparisler sınıfından yeni bir nesne oluşturun
########        order = Siparisler()
########
########        operator_model = AnaOperator.objects.get(AnaOperatorler=operatoru)
########        Tip_operator_model = AltOperator.objects.get(AltOperatorler=tip)
########
########        order.Operator = operator_model
########        order.OperatorTip = Tip_operator_model
########        order.PaketKupur = kontor
########        order.Numara = gsmno
########        if Siparisler.objects.filter(GelenReferans=tekilnumara).exists():
########            sonuc = "Referans numarası daha önce kullanıldı."
########            return sonuc
########        else:
########            order.GelenReferans = tekilnumara
########
########        # Kategori sınıfından ilgili kategoriyi bulun
########        kategori = Kategori.objects.filter(Operatoru=operator_model, KategoriAltOperatoru=Tip_operator_model).first()
########
########        if kategori:
########            # Kontör listesinde ilgili kupur değerine sahip ürünü bulun
########            kontor_urunu = KontorList.objects.filter(Kupur=kontor, Kategorisi=kategori).first()
########            bekliyor = Durumlar.objects.get(durum_id=Durumlar.BEKLIYOR)
########
########            if kontor_urunu:
########                # Ürün bulundu, api1, api2 ve api3 değerlerini siparişe ekle
########                order.api1 = kontor_urunu.api1
########                order.api2 = kontor_urunu.api2
########                order.api3 = kontor_urunu.api3
########                order.SanalKategori = kategori.pk
########                order.Durum = bekliyor # Varsayılan durum
########                order.save()
########
########                sonuc = "Sipariş başarıyla kaydedildi."
########            else:
########                sonuc = "Tanımlı Paket Bulunamadı"
########        else:
########            sonuc = "Kategori Bulunamadı"
########
########    else:
########        sonuc = "Hatalı"
########
########    return sonuc
########

#def ApiZnetSiparisKaydet(request):
#    # Gelen GET isteğindeki değerleri alın
#    bayi_kodu = request.GET.get('bayi_kodu')
#    sifre = request.GET.get('sifre')
#    operatoru = request.GET.get('operator')
#    tip = request.GET.get('tip')
#    kontor = request.GET.get('kontor')
#    gsmno = request.GET.get('gsmno')
#    tekilnumara = request.GET.get('tekilnumara')
#
#    # Gelen değerler doğruysa database'e kaydedin
#    if bayi_kodu and sifre and operatoru and tip and kontor and gsmno and tekilnumara:
#        # Siparisler sınıfından yeni bir nesne oluşturun
#        order = Siparisler()
#
#        operator_model = AnaOperator.objects.get(AnaOperatorler=operatoru)
#        Tip_operator_model = AltOperator.objects.get(AltOperatorler=tip)
#
#        order.Operator = operator_model
#        order.OperatorTip = Tip_operator_model
#        order.PaketKupur = kontor
#        order.Numara = gsmno
#        order.GelenReferans = tekilnumara
#
#        try:
#            order.Durum = 98  # varsayılan durum
#            order.save()
#            Sonuc = "Sipariş başarıyla kaydedildi."
#            return Sonuc
#        except:
#            Sonuc = "Bu İşlem Daha Önce Gönderildi"
#            return Sonuc
#    else:
#        Sonuc = "Hatali"
#        return Sonuc







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
            # Apiler sınıfından şifre bilgilerini alın
            if order.Operator.AnaOperatorler == "vodafone":
                print("girdimki")
                api = Apiler.objects.get(id=8)
                linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu=VodafoneSorgudj&sifre=gerekyok&operator=vodafone&tip=vodafone&kontor=100444&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"
            elif order.Operator == "turkcell":
                api = Apiler.objects.get(id=9)
                linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu=TurkcellSorgudj&sifre=gerekyok&operator=turkcell&tip=turkcell&kontor=100443&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"
            # Belirtilen URL'ye GET isteği gönderin

            gidenRefNumarasi = api.RefNumarasi
            api.RefNumarasi +=1
            api.save
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
                    order.SanalRef = gidenRefNumarasi
                    order.save()
                    api.ApiBakiye -= Decimal(response[3])
                    api.save()
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
    if orders:
        for order in orders:
            # Apiler sınıfından şifre bilgilerini alın
            if order.Operator.AnaOperatorler == "vodafone":
                print("girdimki")
                api = Apiler.objects.get(id=8)
                linki = f"http://{api.SiteAdresi}/servis/tl_kontrol.php?bayi_kodu=VodafoneSorgudj&sifre=VodafoneSorgudj&tekilnumara={order.SanalRef}"
                #linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu=VodafoneSorgudj&sifre=gerekyok&operator=vodafone&tip=vodafone&kontor=100444&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"
            elif order.Operator == "turkcell":
                api = Apiler.objects.get(id=9)
                linki = f"http://{api.SiteAdresi}/servis/tl_servis.php?bayi_kodu=TurkcellSorgudj&sifre=gerekyok&operator=turkcell&tip=turkcell&kontor=100443&gsmno={order.Numara}&tekilnumara={api.RefNumarasi}"





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
    iptal = Durumlar.objects.get(durum_id=Durumlar.IPTAL_EDILDI)
    sorgusutamam = Durumlar.objects.get(durum_id=Durumlar.SorguTamam)
    sorguCevap = Durumlar.objects.get(durum_id=Durumlar.SorguCevap)
    aski = Durumlar.objects.get(durum_id=Durumlar.ISLEMDE)
    Alternatif_Cevap_Bekliyor = Durumlar.objects.get(durum_id=Durumlar.Alternatif_Cevap_Bekliyor)
    Basarili = Durumlar.objects.get(durum_id=Durumlar.Basarili)

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
                    print("NasipGrimesi lazım")
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
                print("Burada Olmam Lazım")
                # GelenAciklama = order.Aciklama
                input("Nasipppp")

                api.ApiBakiye += Decimal(Siparis.SanalTutar)
                Sirasi = Siparis.Gonderim_Sirasi + 1

                if Sirasi == 2:
                    print("Girdim2")
                    YeniApisi = Siparis.api2

                if Sirasi == 3:
                    print("Girdim3")
                    YeniApisi = Siparis.api3

                if not YeniApisi:
                    print("Girdim ?")
                    Siparis.Durum = iptal
                    Siparis.BayiAciklama = "iptal"
                    Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " + api.Apiadi + " Apisinden " + \
                                       response[
                                           1] + "iptal olanApiSirasi:" + str(
                        Siparis.Gonderim_Sirasi) + " Başka Api olmadığı için iptal edildi.\n"
                    Siparis.save()

                else:
                    print("Nasip")

                    Siparis.Durum = AnaPaket
                    Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " + api.Apiadi + " Apisinden " + \
                                       response[1] + " iptal olanApiSirasi:" + str(Siparis.Gonderim_Sirasi) + "\n"
                    Siparis.Gonderim_Sirasi = Sirasi
                    Siparis.save()
                    AnaPaketGonder()



            #        order.Durum = sorgusutamam
            #       # order.Aciklama = GelenAciklama + response[1]
            #        order.SorguPaketID = response[1].replace('|',',')
            #        order.save()
            #        Sonuc = response[1]
            #      return Sonuc
            # else:
            #    order.Durum = 97
            #    order.Aciklama = response[2]
            #    order.save()
            #    Sonuc = response[2]
            #    return Sonuc
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

            linki = f"http://{api.SiteAdresi}/servis/tl_kontrol.php?bayi_kodu={api.Kullanicikodu}&sifre={api.Sifre}&tekilnumara={Siparis.SanalRef}"
            print(linki)
            url = linki

            #   1: olumlu_islem:5.50
            #   2: islemde:5.50
            #   3: iptal_nedeni

            response = requests.get(url)
            response.encoding = "ISO-8859-1"  # doğru kodlamayı burada belirtin
            print(response.text)
            response = response.text.split(":")
            GelenAciklama = Siparis.Aciklama


            if response[0] == "1":

                # Cevabı işleyin ve veritabanına kaydedin
                # ...
                # order.Durum = sorguCevap # Sorgu CEvap olarak güncellenecek
                # alternatifOrder.Aciklama = response[2]     #TODO buraya bayi aciklaması vs girilmesi lazım.
                # alternatifOrder.YuklenecekPaketFiyat = response[3]    #TODO Maliyete işlenmesi ve api fiyatında güncellenmesi lazım.
                Siparis.Durum = Basarili
                print(response[1])
                if response[1] == "":
                    print("NasipGrimesi lazım")
                    Siparis.BayiAciklama = "Basarili"
                else:
                    Siparis.BayiAciklama = response[1]



                Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: " +api.Apiadi+" Apisinden "+ response[1] + "\n"
                Siparis.save()
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
                print("Burada Olmam Lazım")

                api.ApiBakiye += Decimal(Siparis.SanalTutar)
                Sirasi = Siparis.Gonderim_Sirasi +1

                if Sirasi == 2:
                    print("Girdim2")
                    YeniApisi = Siparis.api2

                if Sirasi == 3:
                    print("Girdim3")
                    YeniApisi = Siparis.api3

                if not YeniApisi:
                    print("Girdim ?")
                    Siparis.Durum = iptal
                    Siparis.BayiAciklama = "iptal"
                    Siparis.Aciklama = GelenAciklama + " SitedenGelen Sonuc Mesajı: "+api.Apiadi+" Apisinden " + response[
                        1] + "iptal olanApiSirasi:" + str(Siparis.Gonderim_Sirasi) + " Başka Api olmadığı için iptal edildi.\n"
                    Siparis.save()

                else:
                    print("Nasip")

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
                siparisler.BayiAciklama = siparis.SorguPaketID
                siparis.save()
                return "Oto İPTAL edildi"



        # AnaPaketVar mi Kontrollü

        if siparis_kupur in PaketSorguListesi:
            print("Aranan değer listede var.")
            siparis.AnaPaketVar = True
        else:
            print("Aranan değer listede yok.")
            siparis.AnaPaketVar = False

        # 5- en son o listeyi print ile yazdırıyoruz.
        if len(cikan_idler) > 0:
            print("Siparisin paketi ile uyumlu alternatifler: ", cikan_idler)
            GelenAciklama = siparis.Aciklama
            siparis.Durum = AltPaketID

            GelenAciklama = GelenAciklama + "\n PaketSorgudan Gelen ID = " + siparis.SorguPaketID + "\n"
            siparis.SorguPaketID = ""
            str_cikan_idler = ",".join([str(id) for id in cikan_idler])
            siparis.SorguPaketID = str_cikan_idler

            GelenAciklama = GelenAciklama + "Bulunan Alternatif ID = " + str_cikan_idler + "\n"
            siparis.Aciklama = GelenAciklama
            siparis.save()

        else:
            print("Siparisin paketi ile uyumlu alternatif bulunamadi")
            GelenAciklama = siparis.Aciklama
            siparis.Durum = AnaPaketGonderDurumu

            GelenAciklama = GelenAciklama + "\n PaketSorgudan Gelen ID = " + siparis.SorguPaketID + "\n"
            siparis.SorguPaketID = ""
            print(siparis.AnaPaketVar)
            print("ÜsteBak")

            GelenAciklama = GelenAciklama + "Hiç Eşleşen Alternatif Bulunamadi. Orjinal Paket Yüklemeye Gönderiliyor.\n"
            siparis.Aciklama = GelenAciklama
            siparis.save()
            AnaPaketGonder()





def YuklenecekPaketler(request):
    print("Nasip-00")
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