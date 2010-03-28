from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
# Create your models here.

class StockLog(models.Model):
  type = models.IntegerField()
  date = models.DateTimeField(null=True, blank=True, default=datetime.now)
  quantity = models.PositiveIntegerField()
  user = models.CharField(max_length=255)
  description = models.TextField(null=True, blank=True, verbose_name=_("why?"))
  product = models.ForeignKey(Product, verbose_name=_("product"))

  class Meta:
    verbose_name = _('stock log')
    verbose_name_plural = _('stock logs')
    ordering = ('-date', 'description')

  def __unicode__(self):
    return "Log: %s by %s" % (self.description[:20], self.user)
