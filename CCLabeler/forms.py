from django import forms
from . import utils
from pathlib import Path
class UploadFileForm(forms.Form):
    #name = forms.CharField(max_length=50, label='name')
    userdir = Path(utils.userdir,  label='File')
    CHOICES = [(file.name, file.stem) for file in userdir.glob('*.json')]
    user = forms.ChoiceField(choices=CHOICES, label='User', widget=forms.Select)
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'accept': ".png, .jpg, .jpeg"}))
