from django import forms
from .models import Apiler

class SelectAPIForm(forms.Form):
    selected_api = forms.ChoiceField(label="Selected API", required=False)

    def __init__(self, *args, **kwargs):
        super(SelectAPIForm, self).__init__(*args, **kwargs)
        self.fields['selected_api'].choices = [(str(api.id), str(api)) for api in Apiler.objects.all()]

