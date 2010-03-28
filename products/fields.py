import re
from django import forms 

class CurrencyField (forms.RegexField):
    #currencyRe = re.compile(r'^[0-9]{1,5}(.[0-9][0-9])?$')
    currencyRe = re.compile(r'^[0-9]{1,5}([,\.][0-9][0-9])?$')
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(
            self.currencyRe, None, None, *args, **kwargs)

    def clean(self, value):
        value = super(CurrencyField, self).clean(value)
        #return float(value)
        if value == '':
          return '0.0'
        else:
          return value.replace(',', '.')

class CurrencyInput (forms.TextInput):
    def render(self, name, value, attrs=None):
        if value != '':
            try:
                #value = u"%.2f" % value
                value = (u"%.2f" % value).replace('.', ',')
            except TypeError:
                pass
        return super(CurrencyInput, self).render(name, value, attrs)

