from django import forms
from .models import Apiler

class SelectAPIForm(forms.Form):
    selected_api = forms.ChoiceField(label="Selected APIII", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_api'].choices = [(api.id, str(api)) for api in Apiler.objects.all()]
