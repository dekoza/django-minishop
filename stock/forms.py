from django import forms
from django.utils.translation import ugettext as _
from products.models import Category, Manufacturer
from products.forms import BetterTreeNodeChoiceField

ORDER = [
    ['-', 'descenting'],
    ['', 'ascending'],
    ]
ORDER_CHOICES = [
    ['name', _('name')],
    ['catalogue_number', _('Catalogue number')],
    ['price', _('price')],
    ['quantity', _('quantity')],
    ]

class StockChangeForm(forms.Form):
  quantity = forms.IntegerField()
  #date = forms.DateTimeField()
  description = forms.CharField(required=False, label=_("Why?"), widget=forms.Textarea)
  user = forms.CharField(required=True, label=_("Who?"))

class StockFilterForm(forms.Form):
  def __init__(self, *args, **kwargs):
    super(StockFilterForm, self).__init__(*args, **kwargs)
    self.fields['manufacturer'].choices = [('', '-------')] + [ [m.pk, m.name] for m in Manufacturer.objects.all()]
  query = forms.CharField(required=False, label=_("Search"))
  category = BetterTreeNodeChoiceField(queryset=Category.tree.all(), required=False, empty_label='------') 
  manufacturer = forms.ChoiceField(required=False) 
  order = forms.ChoiceField(choices=ORDER, required=False) 
  order_by = forms.ChoiceField(choices=ORDER_CHOICES, required=False) 
