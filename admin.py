import base64
import re
from django import http, template
from django.contrib.admin import ModelAdmin
from django.contrib.auth import authenticate, login
from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.hashcompat import md5_constructor
from django.contrib.admin.sites import AdminSite
from django.contrib import admin

from customers.models import Customer
from orders.models import Order
from products.models import Product
import simplejson as json
import datetime

class ShopAdminSite(AdminSite):
    """
    An AdminSite object encapsulates an instance of the Django admin application, ready
    to be hooked in to your URLConf. Models are registered with the AdminSite using the
    register() method, and the root() method can then be used as a Django view function
    that presents a full admin interface for the collection of registered models.
    """
    
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = {
                    'add': model_admin.has_add_permission(request),
                    'change': model_admin.has_change_permission(request),
                    'delete': model_admin.has_delete_permission(request),
                }

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
                    }
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': app_label + '/',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(lambda x, y: cmp(x['name'], y['name']))

        recent_customers = Customer.objects.all().order_by('-user__date_joined')[:5]
        recent_orders_count = Order.objects.filter(status=1).count()
        orders_amount = Order.stats.order_amount_by_date() 
        week = datetime.timedelta(weeks=1)
        two_weeks = datetime.timedelta(weeks=2)
        total_volume = Product.stock.total_volume()

        orders_value_current = Order.stats.sale_volume_by_date() 
        orders_value_prev = Order.stats.sale_volume_by_date(start=datetime.date.today()-two_weeks, end=datetime.date.today()-week) 
        for i,o in enumerate(orders_value_current):
          orders_value_prev[i][0] = o[0]

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
            'total_volume': total_volume,
            'recent_customers': recent_customers,
            'recent_orders_count': recent_orders_count,
            'root_path': self.root_path,
            'orders_amount': json.dumps(orders_amount),
            'orders_value_current': json.dumps(orders_value_current),
            'orders_value_prev': json.dumps(orders_value_prev),
        }
        context.update(extra_context or {})
        return render_to_response('admin/index.html', context,
            context_instance=template.RequestContext(request)
        )
    index = never_cache(index)

admin_site = ShopAdminSite()

from django.contrib.flatpages.models import FlatPage
from django import forms
from tinymce.widgets import TinyMCE

class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 75, 'rows': 8}), required=False, label=_("Content"))


class FlatPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']
    form = FlatPageForm

admin_site.register(FlatPage, FlatPageAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'submit_date', 'is_public', 'is_removed']
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['submit_date', 'is_public', 'is_removed']
    date_hierarchy = 'submit_date'
    ordering = ['-submit_date']
    exclude = ['content_type', 'object_pk', 'site', 'user', 'submit_date',
               'ip_address']

from django.contrib.comments.models import Comment
admin_site.register(Comment, CommentAdmin)
