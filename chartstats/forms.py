from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import ugettext_lazy as _

class DefaultDateForm(forms.Form):
  start_date = forms.DateField(widget=AdminDateWidget())
  end_date = forms.DateField(widget=AdminDateWidget())

  def clean(self):
    cleaned_data = self.cleaned_data
    start_date = self.cleaned_data.get('start_date')
    end_date = self.cleaned_data.get('end_date')
    if (start_date and end_date) and (start_date > end_date):
      raise forms.ValidationError("End date is earlier than start date")
    return cleaned_data

