import decimal
from urllib.parse import unquote
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render
from .models import Siparisler, Apiler,AnaOperator,AltOperator,KontorList,Kategori,AlternativeProduct,YuklenecekSiparisler,Durumlar,VodafonePaketler,Bayi_Listesi,BakiyeHareketleri,Turkcell,TTses,TTtam
from .urunleri_cek import *
import requests
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
import environ

from django import forms

from django.shortcuts import render
from django.http import HttpResponseRedirect



#class ApiForm(forms.Form):
#    api1 = forms.ChoiceField(choices=[(api.id, api.Apiadi) for api in Apiler.objects.all()])
#    api2 = forms.ChoiceField(choices=[(api.id, api.Apiadi) for api in Apiler.objects.all()])
#    api3 = forms.ChoiceField(choices=[(api.id, api.Apiadi) for api in Apiler.objects.all()])
#    selected_items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

class ApiForm(forms.Form):
    api1 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False, empty_label="----")
    api2 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False, empty_label="----")
    api3 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False, empty_label="----")
    selected_items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)


    def __init__(self, *args, **kwargs):
        super(ApiForm, self).__init__(*args, **kwargs)
        self.fields['selected_items'].choices = [(kontor.id, kontor.Urun_adi) for kontor in KontorList.objects.all()]


