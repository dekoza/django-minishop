#from django.forms import ModelForm, Form, EmailField, CharField, ChoiceField, BooleanField
from orders.models import PAYMENT_TYPES, SHIPMENT_TYPES
import base64

from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

class PaymentShipment(forms.Form):
  payment = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_TYPES, label=_("payment type"))
  shipment = forms.ChoiceField(widget=forms.RadioSelect, choices=SHIPMENT_TYPES, label=_("shipment type"))
