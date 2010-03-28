from django import forms
from blog.models import *
from tinymce.widgets import TinyMCE
from django.utils.translation import ugettext_lazy as _

class PostForm(forms.ModelForm):
  class Meta:
    model = Post
  body = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("body"))

class CategoryForm(forms.ModelForm):
  class Meta:
    model = Category
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("description"))
