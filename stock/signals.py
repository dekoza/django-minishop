import django.dispatch
from django.utils.translation import ugettext as _

quantity_change = django.dispatch.Signal(providing_args=["instance", "delta"])

DESCRIPTIONS = [
    _("Quantity reduction"),
    _("Quantity increase"),
    ]

def log_stock_change(sender, instance, delta, order=None, meta=None, **kwargs):
  from stock.models import StockLog
  from django.contrib.auth.models import User
  from django.core.urlresolvers import reverse
  print 'delta',delta
  if delta < 0:
    type = 1
  else:
    type = 0
  if order:
    d = _("Automatic quantity reduction for order: ")+"<a href=\""+reverse('review_order',kwargs={'order_id':order.pk})+"\">"+order.name+"</a>"
  else:
    d = DESCRIPTIONS[type]

  if meta:
    user = meta['user']
    d = meta['description']
  else:
    user = _("Shop sprite")
  
  new_log = StockLog(type=type, 
      quantity=instance.quantity,
      user=user, 
      product=instance,
      description=d)
  new_log.save()

quantity_change.connect(log_stock_change)
