from django.contrib import admin
from biolander.admin import admin_site
from slideshow.models import *
from slideshow.forms import *

class SlideAdmin(admin.ModelAdmin):
    form = SlideForm
    list_display = ('name', 'link', 'position', )
    #search_fields = ('email',)
    #list_filter = ('subscribed',)
admin.site.register(Slide, SlideAdmin)
admin_site.register(Slide, SlideAdmin)
