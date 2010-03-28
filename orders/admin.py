from django.contrib import admin
from orders.models import *
from django.utils.translation import ugettext_lazy as _
from biolander.admin import admin_site

class ItemInline(admin.StackedInline):
  model = OrderedItem
  exclude = ('product', 'user', 'status')
  extra = 1

class OrderAdmin(admin.ModelAdmin):
  inlines = [ ItemInline, ]
  exclude = ('name', 'user', 'status')


admin.site.register(Order, OrderAdmin)
admin_site.register(Order, OrderAdmin)
