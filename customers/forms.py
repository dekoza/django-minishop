#from django.forms import ModelForm, Form, EmailField, CharField, ChoiceField, BooleanField
import base64
import re
from django.contrib.auth import authenticate

from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.forms.models import inlineformset_factory, modelformset_factory, formset_factory
from django.forms.util import ErrorList
from customers.models import *
from customers.models import CUSTOMER_TYPES
from django.contrib.localflavor.pl.forms import PLPostalCodeField

ADDRESS_TYPES = (
    (False, _('Private')),
    (True, _('Corporate')),
)

def boolean_coerce(value):
  # value is received as a unicode string
  if str(value).lower() in ( '1', 'true' ):
    return True
  elif str(value).lower() in ( '0', 'false' ):
    return False
  return None

class OrderedForm(object):
	def __init__(self, *args, **kwargs):
		super(OrderedForm, self).__init__(*args, **kwargs)
		if hasattr(self.Meta, 'fields_order'):
			self.fields.keyOrder = self.Meta.fields_order

class InlineAddressForm(OrderedForm, forms.ModelForm):
  class Meta:
    model = Address
    exclude=('is_billing', 'is_shipping', 'customer')
    fields_order = ('is_corporate', 'company_name', 'nip', 'first_name', 'last_name', 'city', 'street', 'house_number', 'postal_code', 'phone_number')
  is_corporate = forms.TypedChoiceField(required=True, widget=forms.RadioSelect, choices=ADDRESS_TYPES, initial=False, coerce=boolean_coerce)
  first_name = forms.CharField(required=False, label=_("first name"), widget=forms.TextInput(attrs={'class':'private_field'}))
  last_name = forms.CharField(required=False, label=_("last name"), widget=forms.TextInput(attrs={'class':'private_field'}))
  company_name = forms.CharField(required=False, label=_("company name"), widget=forms.TextInput(attrs={'class':'corporate_field'}))
  nip = forms.CharField(max_length=13, required=False, label=_("nip"), widget=forms.TextInput(attrs={'class':'corporate_field'}))
  postal_code = PLPostalCodeField(label=_("postal code"))

  def _has_valid_checksum(self, number):
    """
    Calculates a checksum with the provided algorithm.
    """
    multiple_table = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    result = 0
    for i in range(len(number)-1):
      result += int(number[i]) * multiple_table[i]

    result %= 11
    if result == int(number[-1]):
      return True
    else:
      return False

  def clean(self):
    """
    Custom clean method - if address is corporate make company_name and nip required
    """
    cleaned_data = self.cleaned_data
    is_corporate = cleaned_data.get("is_corporate", False)
    is_billing = cleaned_data.get("is_billing", False)
    company_name = cleaned_data.get("company_name", False)
    nip = cleaned_data.get("nip", False)

    regex = re.compile(r'^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{2}-\d{2}-\d{3}-\d{3}$')
    if nip and not regex.search(nip):
      self._errors["nip"] = ErrorList([_("Enter a tax number field (NIP) in the format XXX-XXX-XX-XX or XX-XX-XXX-XXX.")])
      del cleaned_data["nip"]
      return cleaned_data
    if nip and not self._has_valid_checksum(re.sub("[-]", "", nip)):
      self._errors["nip"] = ErrorList([_("Wrong checksum for the Tax Number (NIP).")])
      return cleaned_data

    if is_corporate and not company_name:
      self._errors["company_name"] = ErrorList([_("Company name is required for corporate address")])
      del cleaned_data["company_name"]
    if is_corporate and not nip:
      self._errors["nip"] = ErrorList([_("Tax identification number is required for corporate address")])
      del cleaned_data["nip"]
    return cleaned_data


AddressFormset = formset_factory(InlineAddressForm, extra=2, max_num=2)

class RegistrationForm(OrderedForm, forms.ModelForm):
  class Meta:
    model = Customer
    fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name', 'birthdate')
    fields_order = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'birthdate')
  email = forms.EmailField(required=True, label=_("email"))
  password = forms.CharField(required=True,widget=widgets.PasswordInput(render_value=False), label=_("password"))
  confirm_password = forms.CharField(required=True,widget=widgets.PasswordInput(render_value=False), label=_("confirm password"))
  first_name = forms.CharField(required=True, label=_("first name"))
  last_name = forms.CharField(required=True, label=_("last name"))
  #type = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=CUSTOMER_TYPES, label=_("type"))

  def clean(self):
    """
    Validate passwords - both need to be the same
    """
    cleaned_data = self.cleaned_data
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')
    if password and confirm_password:
      if not password == confirm_password:
        msg = u"Passwords do not match"
        self._errors['password'] = ErrorList([msg])
    return cleaned_data

  def clean_email(self):
    """
    Check for duplicate e-mail since it will be used for login and needs to  be unique
    """
    if User.objects.filter(email__iexact=self.cleaned_data['email']):
      msg = u"This e-mail is already registered in our database"
      self._errors['email'] = ErrorList([msg])
    return self.cleaned_data['email']

  def save(self):
    new_user = Customer.objects.create_inactive_user(username=base64.b64encode(self.cleaned_data['email'])[:30],
        password=self.cleaned_data['password'],
        email=self.cleaned_data['email'],
        first_name=self.cleaned_data['first_name'],
        last_name=self.cleaned_data['last_name'])
    return new_user


class RegistrationConfirmForm(forms.Form):
  accept_licence = forms.BooleanField(required=True, label=_("I agree to the terms of service"))
  accept_newsletter = forms.BooleanField(required=False)


class LoginForm(forms.Form):
  email = forms.EmailField(required=True, label=_("Email"))
  password = forms.CharField(required=True,widget=widgets.PasswordInput(render_value=False), label=_("Password"))
  #next = forms.CharField(required=False,widget=forms.HiddenInput)

  def __init__(self, request=None, *args, **kwargs):
    self.request = request
    self.user_cache = None
    super(LoginForm, self).__init__(*args, **kwargs)

  def clean(self):
    email = self.cleaned_data.get('email')
    password = self.cleaned_data.get('password')
    try:
      username = base64.b64encode(email)[:30]
    except:
      username = None
    if username and password:
      self.user_cache = authenticate(username=username, password=password)
      if self.user_cache is None:
        raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
      elif not self.user_cache.is_active:
        raise forms.ValidationError(_("This account is inactive."))
    if self.request:
      if not self.request.session.test_cookie_worked():
        raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
    return self.cleaned_data

  def get_user(self):
    return self.user_cache

class ProfileChangeForm(forms.ModelForm):
  email = forms.EmailField(required=True)
  #newsletter = forms.BooleanField()
  class Meta:
    model = User
    exclude = ('password', 'last_login', 'date_joined', 'groups', 'user_permissions', 'is_superuser', 'is_active', 'is_staff', 'username',)


class AddressEditForm(OrderedForm, forms.ModelForm):
  class Meta:
    model = Address
    exclude = ('customer',)
    fields_order = ('is_corporate', 'company_name', 'nip', 'first_name', 'last_name', 'city', 'street', 'house_number', 'postal_code', 'phone_number', 'is_billing', 'is_shipping')
  is_corporate = forms.TypedChoiceField(required=True, widget=forms.RadioSelect, choices=ADDRESS_TYPES, initial=False, coerce=boolean_coerce)
  company_name = forms.CharField(required=False, label=_("company name"), widget=forms.TextInput(attrs={'class':'corporate_field'}))
  nip = forms.CharField(max_length=13, required=False, label=_("nip"), widget=forms.TextInput(attrs={'class':'corporate_field'}))
  first_name = forms.CharField(required=False, label=_("first name"), widget=forms.TextInput(attrs={'class':'private_field'}))
  last_name = forms.CharField(required=False, label=_("last name"), widget=forms.TextInput(attrs={'class':'private_field'}))
  postal_code = PLPostalCodeField(label=_("postal code"))

  def _has_valid_checksum(self, number):
    """
    Calculates a checksum with the provided algorithm.
    """
    multiple_table = (6, 5, 7, 2, 3, 4, 5, 6, 7)
    result = 0
    for i in range(len(number)-1):
      result += int(number[i]) * multiple_table[i]

    result %= 11
    if result == int(number[-1]):
      return True
    else:
      return False

  def clean(self):
    """
    Custom clean method - if address is corporate make company_name and nip required
    """
    cleaned_data = self.cleaned_data
    is_corporate = cleaned_data.get("is_corporate", False)
    is_billing = cleaned_data.get("is_billing", False)
    company_name = cleaned_data.get("company_name", False)
    nip = cleaned_data.get("nip", False)

    regex = re.compile(r'^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{2}-\d{2}-\d{3}-\d{3}$')
    if nip and not regex.search(nip):
      self._errors["nip"] = ErrorList([_("Enter a tax number field (NIP) in the format XXX-XXX-XX-XX or XX-XX-XXX-XXX.")])
      del cleaned_data["nip"]
      return cleaned_data
    if nip and not self._has_valid_checksum(re.sub("[-]", "", nip)):
      self._errors["nip"] = ErrorList([_("Wrong checksum for the Tax Number (NIP).")])
      return cleaned_data

    if is_corporate and not company_name:
      self._errors["company_name"] = ErrorList([_("Company name is required for corporate address")])
      del cleaned_data["company_name"]
    if is_corporate and not nip:
      self._errors["nip"] = ErrorList([_("Tax identification number is required for corporate address")])
      del cleaned_data["nip"]
    return cleaned_data

