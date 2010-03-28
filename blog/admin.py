from django.contrib import admin
from blog.models import *
from blog.forms import *
from tinymce.widgets import TinyMCE
from django.db import models
from biolander.admin import admin_site

class PostAdmin(admin.ModelAdmin):
  form = PostForm
  prepopulated_fields = {"slug": ("title",)}
  list_display = ( 'title', 'is_published', 'created', 'modified')
  list_filter = ('is_published', 'categories', 'created', 'modified')
  filter_horizontal = ('categories',)
  fieldsets = (
      ('Basic info', {
        'fields': (('title', 'slug'), ('is_published', 'frontpage'), 'body', 'categories') 
        }), 
      )
  #formfield_overrides = {
  #   models.TextField: {'widget': TinyMCE},
  #   }

class CategoryAdmin(admin.ModelAdmin):
  form = CategoryForm
  prepopulated_fields = {"slug": ("name",)}

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)

admin_site.register(Post, PostAdmin)
admin_site.register(Category, CategoryAdmin)
