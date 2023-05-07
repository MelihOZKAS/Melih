import requests
from .models import Apiler, ApidenCekilenPaketler,AnaOperator,AltOperator,Kategori
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
            GelenPaket = Kategori.objects.get(KategoriAdi=bilgiler[0])
            if GelenPaket.exists():
                # güncelleme işlemi yapılır
                anaOperatorleriGuncelle = GelenPaket.first()

                OperatorleriGuncelle.Operatoru = bilgiler[1]
                OperatorleriGuncelle.KategoriAltOperatoru = bilgiler[2]
                OperatorleriGuncelle.GorunecekName = bilgiler[3]
                OperatorleriGuncelle.GorunecekSira = bilgiler[4]
                OperatorleriGuncelle.Aktifmi = True
                OperatorleriGuncelle.save()

            else:
                # yeni kayıt oluşturma işlemi yapılır
                paketEkle = AnaOperator(
                    KategoriAdi = bilgiler[0],
                    Operatoru = bilgiler[1],
                    KategoriAltOperatoru = bilgiler[2],
                    GorunecekName = bilgiler[3],
                    GorunecekSira = bilgiler[4],
                    Aktifmi = True
                )
                paketEkle.save()

    return "Nasip" +response.text
