from django.contrib import admin
from biolander.admin import admin_site
from newsletter.models import Subscription
from newsletter.forms import SubscriptionForm

class SubscriptionAdmin(admin.ModelAdmin):
    
    list_display = ('email', 'subscribed', 'created_on', )
    search_fields = ('email',)
    list_filter = ('subscribed',)
    
admin.site.register(Subscription, SubscriptionAdmin)
admin_site.register(Subscription, SubscriptionAdmin)
