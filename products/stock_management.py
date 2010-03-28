from django.db import models
from biolander.stock.signals import quantity_change

class StockManager(models.Manager):
  def total_volume(self, set=None):
    from django.db import connection
    cursor = connection.cursor()
    sql = """
    SELECT SUM(price*quantity) AS total_volume 
    FROM products_product
    """
    if set:
      ids = set.join(",")
      limit = """
      WHERE id in (%s)
      """ % ids
      sql += limit
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

def stock_logger(sender, **kwargs):
  instance = kwargs['instance']
  order = getattr(instance, '_order_cache', None)
  meta = getattr(instance, '_stock_log_meta', None)
  id = instance.pk
  try:
    old_instance = sender.objects.get(pk=id)
    delta = old_instance.quantity - instance.quantity
  except:
    old_instance = None
    delta = 0
  if not delta == 0 and old_instance:
    quantity_change.send(sender=sender, instance=instance, delta=delta, order=order, meta=meta)
