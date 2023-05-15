from django import forms
from .models import Apiler

class SelectAPIForm(forms.Form):
    api_choice = forms.ModelChoiceField(queryset=Apiler.objects.all())
