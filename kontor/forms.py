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



class ApiForm(forms.Form):
    api1 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False)
    api2 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False)
    api3 = forms.ModelChoiceField(queryset=Apiler.objects.all(), required=False)
    selected_items = forms.CharField(widget=forms.HiddenInput)