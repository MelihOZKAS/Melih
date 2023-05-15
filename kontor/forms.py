from django import forms
from .models import Apiler

class SelectAPIForm(forms.Form):
    apiler = [(api.id, str(api)) for api in Apiler.objects.all()]
    selected_api = forms.ChoiceField(label="Selected API", choices=apiler, required=True)


