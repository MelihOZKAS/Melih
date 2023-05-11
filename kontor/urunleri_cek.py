import requests
from django.http import HttpResponse
from .models import Apiler, ApidenCekilenPaketler,AnaOperator,AltOperator,Kategori,KontorList
from decimal import Decimal
import json



def paketlericekgrafi(Api,siteadi,kullanicikodu,kullaniciadi,sifre):
    print(str(Api)+siteadi+kullanicikodu+kullaniciadi+sifre)
    url = f"https://{siteadi}/api/paket_listesi.asp?bayikodu={kullanicikodu}&kadi={kullaniciadi}&sifre={sifre}"
    response = requests.get(url).text
    print(response)
    # Tüm ApidenCekilenPaketler kayıtlarını sil
    ApidenCekilenPaketler.objects.filter(apiler=Api).delete()

    gelenUrunler = response.split(';')

    AradakiHesaplayici = 1
    for i in gelenUrunler:

        if AradakiHesaplayici == 1:
            paketAdi = i
        if AradakiHesaplayici == 2:
            paketKupur = i
        if AradakiHesaplayici == 3:
            Sabitbes = i
        if AradakiHesaplayici == 4:
            SabitSifir = i
        if AradakiHesaplayici == 5:
            kupurFiyati = i
            kupurFiyatiYeni =  kupurFiyati.strip().replace(",", ".")
            grafiTutar = Decimal(kupurFiyatiYeni)
        if AradakiHesaplayici == 6:
            Tipi = i
        if AradakiHesaplayici == 7:
            bayiKupur = i


        AradakiHesaplayici +=1

        if AradakiHesaplayici == 8:
            AradakiHesaplayici = 1
            ApidenCekilenPaketler.objects.create(
                apiler=Api,
                urun_adi=paketAdi,
                kupur=paketKupur,
                ApiGelen_fiyati=grafiTutar,
                ApiGelen_operator_adi="Yok",
                ApiGelen_operator_tipi=Tipi
            )




def paketlericekGenco(Api,siteadi,kullanicikodu,kullaniciadi,sifre):
    import requests

    url = f'http://{siteadi}/ClientWebService'
    data = {'Operation': 'TopUpPrices',
            'request[DealerCode]': f'{kullanicikodu}',
            'request[Username]': f'{kullaniciadi}',
            'request[Password]': f'{sifre}'}

    response = requests.post(url, data=data)
    print(response.text)

    # Tüm ApidenCekilenPaketler kayıtlarını sil
    ApidenCekilenPaketler.objects.filter(apiler=Api).delete()

    response_dict = json.loads(response.text)

    # Paket bilgilerini yazdır
    for package in response_dict['TopUpPricesResult']['Packages']:
        PaketAdi = package['PackageName']
        paketID = package['ProductId']
        Fiyati = package['Price']
        Operator = package['Operator']
        Type = package['Type']
        Fiyati = Fiyati.strip().replace(",", ".")

        print(PaketAdi)
        print(paketID)
        print(Fiyati)
        print(Operator)
        print(Type)
        print(Fiyati)

        # if not ApidenCekilenPaketler.objects.filter(apiler=Api, kupur=paketKupur).exists():
        ApidenCekilenPaketler.objects.create(
            apiler=Api,
            urun_adi=PaketAdi,
            kupur=paketID,
            ApiGelen_fiyati=Fiyati,
            ApiGelen_operator_adi=Operator,
            ApiGelen_operator_tipi=Type
        )





def AltOperatorleriCek():
    response = requests.post('http://92.205.129.63:4244/Sorgu.php', data={
        'python': 'altop'
    })

    if response.status_code == 200:
        data = response.content.decode('utf-8')
        altopS = data.split('|')
        for altOP in altopS:
            if not altOP.strip():
                continue
            GelenPaket = AltOperator.objects.filter(AltOperatorler=altOP)
            if GelenPaket.exists():
                # güncelleme işlemi yapılır
                altOperatorleriGuncelle = GelenPaket.first()
                altOperatorleriGuncelle.AltOperatorler = altOP
                altOperatorleriGuncelle.save()

            else:
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = AltOperator(
                    AltOperatorler=altOP
                )
                paketEkle.save()




def AnaOperatorleriCek():
    response = requests.post('http://92.205.129.63:4244/Sorgu.php', data={
        'python': 'anaop'
    })

    if response.status_code == 200:
        data = response.content.decode('utf-8')
        anaopS = data.split('|')
        for anaOP in anaopS:
            if not anaOP.strip():
                continue
            GelenPaket = AnaOperator.objects.filter(AnaOperatorler=anaOP)
            if GelenPaket.exists():
                # güncelleme işlemi yapılır
                anaOperatorleriGuncelle = GelenPaket.first()
                anaOperatorleriGuncelle.AnaOperatorler = anaOP
                anaOperatorleriGuncelle.save()

            else:
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = AnaOperator(
                    AnaOperatorler=anaOP
                )
                paketEkle.save()


def OperatorleriCek(request):
    response = requests.post('http://92.205.129.63:4244/Sorgu.php',
                             data={'python': 'Operatorler'})

    print(response.text)
    if response.status_code == 200:
        data = response.content.decode('utf-8')
        operatorler = data.split('|')
        for operatorParcalari in operatorler:
            if not operatorParcalari.strip():
                continue
            print(operatorler)
            bilgiler = operatorParcalari.split('-')
           # GelenPaket = Kategori.objects.filter(KategoriAdi=bilgiler[0])
            #GelenPaket = Kategori.objects.get(KategoriAdi=bilgiler[0])
            gelenAnaOperator = AnaOperator.objects.get(pk=int(bilgiler[1]))
            gelenAltOperator = AltOperator.objects.get(pk=int(bilgiler[2]))


            GelenPaket = Kategori.objects.filter(KategoriAdi=bilgiler[0])
            if GelenPaket.exists():
                # güncelleme işlemi yapılır
                OperatorleriGuncelle = GelenPaket.first()
                OperatorleriGuncelle.Operatoru = gelenAnaOperator
                OperatorleriGuncelle.KategoriAltOperatoru = gelenAltOperator
                OperatorleriGuncelle.GorunecekName = bilgiler[3]
                OperatorleriGuncelle.GorunecekSira = bilgiler[4]
                OperatorleriGuncelle.Aktifmi = True
                OperatorleriGuncelle.save()

            else:
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = Kategori(
                    KategoriAdi = bilgiler[0],
                    Operatoru = gelenAnaOperator,
                    KategoriAltOperatoru = gelenAltOperator,
                    GorunecekName = bilgiler[3],
                    GorunecekSira = bilgiler[4],
                    Aktifmi = True
                )
                paketEkle.save()

    return "Nasip" +response.text

def TurkcellPaketleriSunucudanCek(request):
    eklenen_paketler = []
    silinen_paketler = []
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
            paketGB = float(bilgiler[3]) * 1000
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

            KategorisiGelen = Kategori.objects.get(pk=1)  # TODO 1 yaptım bu Turkcell çünkü
            api1 = Apiler.objects.get(pk=8)
            api2 = Apiler.objects.get(pk=11)
            api3 = Apiler.objects.get(pk=2)
            SatisFiyat = paketFiyat + Decimal('5.00')
            GelenPaket = KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID)
            if GelenPaket.exists():
                # print("Paket ---Update girdim")
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
                PaketiGuncelle.api1 = api1
                PaketiGuncelle.api2 = api2
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
                    api3=api3,
                    zNetKupur=znetFix,
                    AlternatifYapilmasin=alternatifyapilmasin
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

    return f'İşlem tamamlandı.Turkcell Ses Eklenen paketler: {eklenen_paketler}, silinen paketler: {silinen_paketler}'
def VodafonePaketleriSunucudanCek(request):
    eklenen_paketler = []
    silinen_paketler = []
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
            KategorisiGelen = Kategori.objects.get(pk=3)  # TODO 3 yaptım bu Vodafone çünkü
            api1 = Apiler.objects.get(pk=6)
            api2 = Apiler.objects.get(pk=3)
            api3 = Apiler.objects.get(pk=1)
            SatisFiyat = paketFiyat + Decimal('5.00')
            GelenPaket = KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID)
            if GelenPaket.exists():
                # print("Paket ---Update girdim")
                # güncelleme işlemi yapılır
                PaketiGuncelle = GelenPaket.first()
                if PaketiGuncelle.Kupur == Decimal("4124"):
                    PaketNames = "Tüm Dünya 1 Saat"
                if PaketiGuncelle.Kupur == Decimal("4401"):
                    PaketNames = "Kolay Paket 9"
                if PaketiGuncelle.Kupur == Decimal("4402"):
                    PaketNames = "Kolay Paket 14"
                if PaketiGuncelle.Kupur == Decimal("4405"):
                    PaketNames = "Kolay Paket 7"
                if PaketiGuncelle.Kupur == Decimal("4406"):
                    PaketNames = "Kolay Paket 6"
                if PaketiGuncelle.Kupur == Decimal("4407"):
                    PaketNames = "Kolay Paket 12"
                if PaketiGuncelle.Kupur == Decimal("4780"):
                    PaketNames = "Haftalık 500 DK"
                if PaketiGuncelle.Kupur == Decimal("12039"):
                    PaketNames = "Kolay Paket 3 Ay 30 GB"
                if PaketiGuncelle.Kupur == Decimal("13189"):
                    PaketNames = "Kolay Paket 6 Ay 60 GB"
                if PaketiGuncelle.Kupur == Decimal("13315"):
                    PaketNames = "Kolay Paket 16"
                if PaketiGuncelle.Kupur == Decimal("13318"):
                    PaketNames = "Kolay Paket 5"
                if PaketiGuncelle.Kupur == Decimal("13319"):
                    PaketNames = "Kolay Gani 1500 DK"
                if PaketiGuncelle.Kupur == Decimal("13323"):
                    PaketNames = "Kolay Paket 25"
                if PaketiGuncelle.Kupur == Decimal("13402"):
                    PaketNames = "Kolay Paket 3 Ay 45 GB"
                if PaketiGuncelle.Kupur == Decimal("4294"):
                    PaketNames = "Haftalık 3 GB"
                if PaketiGuncelle.Kupur == Decimal("6912"):
                    PaketNames = "Haftalık 5 GB"
                if PaketiGuncelle.Kupur == Decimal("6911"):
                    PaketNames = "Haftalık 10 GB"
                if PaketiGuncelle.Kupur == Decimal("4123"):
                    PaketNames = "Haftalık 1 GB"
                if PaketiGuncelle.Kupur == Decimal("4116"):
                    PaketNames = "Haftalik Sinrisiz Iletisim Paketi"
                if PaketiGuncelle.Kupur == Decimal("4117"):
                    PaketNames = "Haftalik Sinrisiz Sosyal Medya Paketi"
                if PaketiGuncelle.Kupur == Decimal("4118"):
                    PaketNames = "Haftalik Sinrisiz Video Paketi"
                if PaketiGuncelle.Kupur == Decimal("5151"):
                    PaketNames = "Haftalik Sinrisiz TikTok Paketi"
                if PaketiGuncelle.Kupur == Decimal("5150"):
                    PaketNames = "Haftalik Sinrisiz Eglence Paketi"
                if PaketiGuncelle.Kupur == Decimal("4280"):
                    PaketNames = "Gunluk Sinrisiz Iletisim Paketi"
                if PaketiGuncelle.Kupur == Decimal("4279"):
                    PaketNames = "Gunluk Sinrisiz Video Paketi"
                if PaketiGuncelle.Kupur == Decimal("5152"):
                    PaketNames = "15 Gunluk Sinirsiz TikTok"
                if PaketiGuncelle.Kupur == Decimal("11716"):
                    PaketNames = "Süper Kolay Paket 6"
                if PaketiGuncelle.Kupur == Decimal("10394"):
                    PaketNames = "3 Aylik Kolay Paket 50"
                if PaketiGuncelle.Kupur == Decimal("10392"):
                    PaketNames = "Kolay Yeni Paket 25"
                if PaketiGuncelle.Kupur == Decimal("13366"):
                    PaketNames = "Super Kolay Paket 10"
                if PaketiGuncelle.Kupur == Decimal("13278"):
                    PaketNames = "Super Kolay Paket 5"
                if PaketiGuncelle.Kupur == Decimal("7021"):
                    PaketNames = "Süper Kolay Paket 15"
                if PaketiGuncelle.Kupur == Decimal("6658"):
                    PaketNames = "Süper Kolay Paket 15*"
                if PaketiGuncelle.Kupur == Decimal("6972"):
                    PaketNames = "Süper Kolay Paket 1500 DK"
                if PaketiGuncelle.Kupur == Decimal("11716"):
                    PaketNames = "Süper Kolay Paket 6"
                if PaketiGuncelle.Kupur == Decimal("7354"):
                    PaketNames = "54 TL Telsiz Kullanım Ücreti"
                if PaketiGuncelle.Kupur == Decimal("8703"):
                    PaketNames = "18 TL Telsiz Kullanım Ücreti"
                if PaketiGuncelle.Kupur == Decimal("7353"):
                    PaketNames = "36 TL Telsiz Kullanım Ücreti"
                if PaketiGuncelle.Kupur == Decimal("7355"):
                    PaketNames = "72 TL Telsiz Kullanım Ücreti"

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
                PaketiGuncelle.api1 = api1
                PaketiGuncelle.api2 = api2
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
                    AlternatifYapilmasin=alternatifyapilmasin
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

    return f'İşlem tamamlandı. Vodafone Ses Eklenen paketler: {eklenen_paketler}, silinen paketler: {silinen_paketler}'

def TTPaketleriSunucudanCek(request):
    eklenen_paketler=[]
    silinen_paketler=[]
    response = requests.post('http://92.205.129.63:4244/Sorgu.php', data={
        'python': 'PaketCekTTsesAll'
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
            paketGB = float(bilgiler[3])*1000
            paketSMS = float(bilgiler[4])
            paketFiyat = str(bilgiler[5]).replace(" ", "").replace(",", ".")
            paketFiyat = float(paketFiyat)
            paketFiyat = Decimal(paketFiyat)

            paketDay = float(bilgiler[6])
            #znetFix = Decimal(bilgiler[7]) if bilgiler[7].strip() and bilgiler[7] != 'Bulamadım.' else Decimal('0.00')
            if bilgiler[7] == "evet":
                alternatif_bilgisi = True
            else:
                alternatif_bilgisi = False
            alternatifyapilmasin = alternatif_bilgisi
            PaketNames = bilgiler[8]

            KategorisiGelen = Kategori.objects.get(pk=4)   #TODO 4 yaptım bu TT çünkü
            api1 = Apiler.objects.get(pk=2)
            api2 = Apiler.objects.get(pk=11)
            api3 = Apiler.objects.get(pk=2)
            SatisFiyat = paketFiyat + Decimal('5.00')
            GelenPaket = KontorList.objects.filter(Kategorisi=KategorisiGelen, Kupur=paketID)
            if GelenPaket.exists():
                #print("Paket ---Update girdim")
                # güncelleme işlemi yapılır
                PaketiGuncelle = GelenPaket.first()
                PaketiGuncelle.Urun_adi = PaketNames
                PaketiGuncelle.Urun_Detay = Paket
                PaketiGuncelle.Kupur = paketID
                #PaketiGuncelle.zNetKupur = znetFix
                PaketiGuncelle.GunSayisi = paketDay
                PaketiGuncelle.MaliyetFiyat = paketFiyat
                PaketiGuncelle.SatisFiyat = SatisFiyat
                PaketiGuncelle.HeryoneDK = paketDK
                PaketiGuncelle.Sebekeici = Decimal('0.00')
                PaketiGuncelle.internet = paketGB
                PaketiGuncelle.SMS = paketSMS
                PaketiGuncelle.api1 = api1
                #PaketiGuncelle.api2 = api2
                #PaketiGuncelle.api3 = api3
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
                 #   api2=api2,
                 #   api3=api3,
                 #   zNetKupur=znetFix,
                    AlternatifYapilmasin = alternatifyapilmasin
                )
                paketEkle.save()

    # Vodafoneye ait Mevcut paketleri veritabanından getir
    KategorisiGelen = Kategori.objects.get(pk=4)
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

    return f'İşlem tamamlandı. TT Ses Eklenen paketler: {eklenen_paketler}, silinen paketler: {silinen_paketler}'