from django.contrib import admin
from biolander.admin import admin_site
from django.utils.translation import ugettext_lazy as _
from resellers.models import Partner

class PartnerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'code', 'is_active',
                    'last_paid', 'created', 'total_income',
                    'total_unpaid_income', 'earned_today')
    list_filter = ('is_active', 'created', 'last_paid')

admin.site.register(Partner, PartnerAdmin)
admin_site.register(Partner, PartnerAdmin)
