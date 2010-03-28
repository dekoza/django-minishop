from django.contrib import admin
from customers.models import *
from tinymce.widgets import TinyMCE
from biolander.admin import admin_site

class AddressInline(admin.StackedInline):
  model = Address
  extra = 1

class CustomerAdmin(admin.ModelAdmin):
  inlines = [ AddressInline, ] 
  list_display = ['last_name', 'first_name', 'email', 'active', 'newsletter', 'shipping_address', 'joined']
  list_display_links = ['last_name', 'first_name', 'email']
  list_filter = ['type', 'newsletter']
  search_fields = ['user__first_name', 'user__last_name', 'user__email', 'company_name']
  list_select_related = True
  exclude = ('user',)

admin.site.register(Customer, CustomerAdmin)

admin_site.register(Customer, CustomerAdmin)
