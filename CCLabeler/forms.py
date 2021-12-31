from django import forms
from . import utils
from pathlib import Path
class UploadFileForm(forms.Form):
    #name = forms.CharField(max_length=50, label='name')
    userdir = Path(utils.userdir)
    CHOICES = [(file.name, file.name) for file in userdir.glob('*.json')]
    user = forms.ChoiceField(choices=CHOICES, label='user', widget=forms.Select)
    file = forms.FileField()
