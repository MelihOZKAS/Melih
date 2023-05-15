from django import forms
from .models import Apiler

class SelectAPIForm(forms.Form):
    selected_api = forms.ModelChoiceField(queryset=Apiler.objects.all())
