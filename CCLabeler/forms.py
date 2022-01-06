from django import forms
from . import utils
from pathlib import Path


class UploadFileForm(forms.Form):
    # name = forms.CharField(max_length=50, label='name')
    print('====>',forms.Form)
    userdir = Path(utils.userdir, label='File')
    print('userdir:', type(userdir), userdir)
    CHOICES = []
    for file in userdir.glob('*.json'):
        file_name = file.name
        file_stem = file.stem
        print('file_name:', type(file_name), file_name)
        if file_name not in ['golden.json', 'admin.json']:
            CHOICES.append((file_name, file_stem))
    # CHOICES = [(file.name, file.stem) for file in userdir.glob('*.json')]
    user = forms.ChoiceField(choices=CHOICES, label='User', widget=forms.Select)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
