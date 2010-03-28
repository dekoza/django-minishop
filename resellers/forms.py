from django import forms
from django.http import Http404
from resellers.models import Partner
from customers.models import Address
from django.forms.util import ErrorList

class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #if not user:
            #raise Http404
        self.user = kwargs.pop('user')
        address_queryset = Address.published.filter(customer__user=self.user)
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['address'] = forms.ModelChoiceField(
            queryset=address_queryset,
            widget=forms.RadioSelect,
            initial=address_queryset[0]
        )

    def clean_address(self):
        customer = self.user.get_profile()
        adr = self.cleaned_data['address']
        if not adr in customer.address_set.all():
            self._errors['address'] = ErrorList([_("Invalid address")])
        return self.cleaned_data['address']

    class Meta:
        model = Partner
        exclude = ('code', 'user', 'rate', 'is_active',)

