from django.contrib import admin
from products.models import *
from products.forms import *
from tinymce.widgets import TinyMCE
from django.db import models
from biolander.admin import admin_site
from django.utils.translation import ugettext_lazy as _

class ManufacturerAdmin(admin.ModelAdmin):
  form = ManufacturerForm
  fieldsets = (
      (_('basic info'), {
        'fields': (('name', 'slug'), 'logo'),
        # fajny bajer: htmlik nad trescia fieldsetu - moze sie przydac :)
        #'description': 'bla bla bla'
        }), 
      (_('extra info'), {
        'fields':('description',) 
        }),
      )
  prepopulated_fields = {"slug": ("name",)}

class CertificateAdmin(admin.ModelAdmin):
  form = CertificateForm
  fieldsets = (
      (_('basic info'), {
        'fields': (('name', 'slug'), 'logo') 
        }), 
      (_('extra info'), {
        'fields':('description',) 
        }),
      )
  prepopulated_fields = {"slug": ("name",)}

class CategoryAdmin(admin.ModelAdmin):
  form = CategoryForm
  fieldsets = (
      (_('basic info'), {
        'fields': (('name', 'slug'), 'old_id', 'parent', 'image') 
        }), 
      (_('extra info'), {
        'fields':('description',) 
        }),
      )
  prepopulated_fields = {"slug": ("name",)}

class SolutionAdmin(admin.ModelAdmin):
  form = SolutionForm
  fieldsets = (
      (_('basic info'), {
        'fields': (('name', 'slug'), 'parent') 
        }), 
      (_('extra info'), {
        'fields':('description',) 
        }),
      )
  prepopulated_fields = {"slug": ("name",)}
  #class Media:
  #  js = ['/admin_media/tinymce/jscripts/tiny_mce/tiny_mce.js', '/admin_media/tinymce_setup/tinymce_setup.js',]

class ProductAdmin(admin.ModelAdmin):
  form = ProductForm
  fieldsets = (
      (_('basic info'), {
        'fields': (('name', 'slug'), 'old_id', 'catalogue_number', ('price', 'wholesale_price', 'quantity',), 'availibility', ('capacity', 'capacity_type',), ('is_published', 'is_gift'), 'created') 
        }), 
      (_('product taxonomy'), {
        'fields': ('manufacturer', 'certificates', ('categories', 'solutions')) 
        }), 
      (_('product photos'), {
        'fields': ('photos',) 
        }), 
      (_('product details'), {
        #'classes': ('collapse-open',),
        'fields': ('description', 'usage', 'ingredients', ) 
        }), 
      )
  #filter_horizontal = ('certificates',)
  list_display = ( 'name', 'catalogue_number', 'product_thumbnail', 'price', 'quantity', 'manufacturer')
  list_filter = ('is_published', 'manufacturer', 'categories', 'created', 'modified', 'is_gift')
  prepopulated_fields = {"slug": ("name",)}
  #class Media:
  #  js = ['/admin_media/tinymce/jscripts/tiny_mce/tiny_mce.js', '/admin_media/tinymce_setup/tinymce_setup.js',]
  #formfield_overrides = {
  #   models.CharField: {'widget': TinyMCE},
  #   }


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Certificate, CertificateAdmin)

admin_site.register(Product, ProductAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Solution, SolutionAdmin)
admin_site.register(Manufacturer, ManufacturerAdmin)
admin_site.register(Certificate, CertificateAdmin)
