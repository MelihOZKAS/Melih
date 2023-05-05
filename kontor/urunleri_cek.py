import requests
from .models import Apiler, ApidenCekilenPaketler
from decimal import Decimal



def paketlericekgrafi(Api,siteadi,kullanicikodu,kullaniciadi,sifre):
    print(str(Api)+siteadi+kullanicikodu+kullaniciadi+sifre)
    url = f"https://{siteadi}/api/paket_listesi.asp?bayikodu={kullanicikodu}&kadi={kullaniciadi}&sifre={sifre}"
    response = requests.get(url).text
    print(response)

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

            #print(str(Api)+paketAdi+paketKupur+grafiTutar+Tipi)
            #if not ApidenCekilenPaketler.objects.filter(apiler=Api, kupur=paketKupur).exists():
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
            'request[DealerCode]': ''+{kullanicikodu}+'',
            'request[Username]': f'{kullaniciadi}',
            'request[Password]': f'{sifre}'}

    response = requests.post(url, data=data)
    print(response.text)
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
