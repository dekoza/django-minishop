from django import forms
from products.models import *
from products.fields import *
from mptt.forms import TreeNodeChoiceField
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput
from django.forms.models import modelformset_factory

from django.utils.translation import ugettext_lazy as _

# better tree node choice field includes
from django.utils.encoding import smart_unicode
from tinymce.widgets import TinyMCE

# checkbox tree includes
from itertools import chain
from django.utils.html import escape, conditional_escape
from django.utils.translation import ugettext
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe

class BetterTreeNodeChoiceField(TreeNodeChoiceField):
    """A ModelChoiceField for tree nodes. Allows adding root items when specified empty_label kwarg"""
    def __init__(self, level_indicator=u'---', *args, **kwargs):
        self.level_indicator = level_indicator
        if 'empty_label' not in kwargs:
          kwargs['empty_label'] = None
        super(TreeNodeChoiceField, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """
        Creates labels which represent the tree level of each node when
        generating option labels.
        """
        return u'%s %s' % (self.level_indicator * getattr(obj,
                                                  obj._meta.level_attr),
                           smart_unicode(obj))

class ModelTreeChoiceField(forms.ModelMultipleChoiceField):
    """
    Makes a ModelMultipleChoiceField add level prefix to each label
    """
    def label_from_instance(self, obj):
        """
        Creates labels which represent the tree level of each node when
        generating option labels.
        """
        return u'%s %s' % ('--' * getattr(obj,
                                                  obj._meta.level_attr),
                           smart_unicode(obj))

class CheckboxTree(forms.CheckboxSelectMultiple):
    class Media:
        css = {
            'all': ('css/tree.css',)
        }

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul class="tree">']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
  price = CurrencyField(widget=CurrencyInput, initial=50, label=_('Price'))
  wholesale_price = CurrencyField(widget=CurrencyInput, initial=50, label=_('Wholesale price (EURO)'), required=False)
  certificates = forms.ModelMultipleChoiceField(queryset=Certificate.objects.all(), widget=CheckboxTree, label=_("Certificates"), required=False)
  categories = ModelTreeChoiceField(queryset=Category.tree.all(), widget=CheckboxTree, label=_("Categories"))
  solutions = ModelTreeChoiceField(queryset=Solution.tree.all(), widget=CheckboxTree, label=_("Solutions"))
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Description"))
  usage = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Usage"))
  ingredients = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Ingredients"))
  old_id = forms.IntegerField(required=False)
  #created = forms.DateTimeField(widget=forms.DateTimeInput())
  class Media:
    css = { 'all' : ('css/product.css',), }

class CategoryForm(forms.ModelForm):
  class Meta:
    model = Category
  parent = BetterTreeNodeChoiceField(queryset=Category.tree.all(), required=False, label=_("Parent"))
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Description"))


class SolutionForm(forms.ModelForm):
  class Meta:
    model = Solution
  parent = BetterTreeNodeChoiceField(queryset=Solution.tree.all(), required=False, label=_("Parent"))
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Description"))

class ManufacturerForm(forms.ModelForm):
  class Meta:
    model = Manufacturer
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Description"))

class CertificateForm(forms.ModelForm):
  class Meta:
    model = Certificate
  description = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Description"))

class CategoryRecomendationsForm(forms.Form):
    category = BetterTreeNodeChoiceField(queryset=Category.tree.all(),
                                         required=False, label=_("Category"),
                                         empty_label="---")
    count = forms.IntegerField(widget=forms.HiddenInput, required=True)
