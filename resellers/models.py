from django.db import models
from customers.models import Address
from orders.models import Order
from resellers.managers import HistoryManager
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

class Partner(models.Model):
    code = models.CharField(max_length=7, unique=True)
    user = models.ForeignKey(User, unique=True, verbose_name=_("user"))
    address = models.ForeignKey(Address)
    rate = models.DecimalField(max_digits=8, decimal_places=2, default="0.05")
    account = models.TextField()
    is_active = models.BooleanField(default=False, verbose_name=_("Is aprooved"))

    last_paid = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    def save(self):
        if not self.pk:
            # generate the unique partner code
            # it consist of the user's id and first name/surname letters
            number = "-%04d" % self.user.pk
            code = self.user.first_name.lower()[:1]+self.user.last_name.lower()[:1]+number
            self.code = code
        super(Partner, self).save()

    @property
    def total_income(self):
        return PartnerHistory.objects.total_income(self)

    @property
    def total_unpaid_income(self):
        return PartnerHistory.objects.unpaid_income(self)

    @property
    def earned_today(self):
        return PartnerHistory.objects.earned_today(self)

    @property
    def full_name(self):
        return self.user.first_name+" "+self.user.last_name


class PartnerHistory(models.Model):
    partner = models.ForeignKey(Partner)
    order = models.ForeignKey(Order)
    income = models.DecimalField(max_digits=8, decimal_places=2,
                                 verbose_name=_("income"))
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    objects = HistoryManager()
