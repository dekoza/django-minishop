from django import forms
from tinymce.widgets import TinyMCE

class SlideForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False)
