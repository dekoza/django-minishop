from django.db import models
import datetime, calendar

class StatManager(models.Manager):
  def low_on_stock(self):
    """
    Returns a queryset of items that are low on stock
    """
    from django.db import connection
    from orders.models import Order
    cursor = connection.cursor()
    sql = """
    SELECT ord.id 
    FROM orders_order ord
    JOIN orders_ordereditem itm ON itm.order_id = ord.id
    JOIN products_product prd ON itm.product_id = prd.id
    WHERE ord.status != 5 AND itm.quantity >= prd.quantity
    """
    cursor.execute(sql)
    ids = [id[0] for id in cursor.fetchall()]
    return Order.objects.filter(pk__in=ids)

  def sale_volume_by_date(self, start=datetime.date.today()+datetime.timedelta(weeks=-1), end=datetime.date.today()):
    """
    Returns list of lists: [sale_sum_for_the_day, js_timestamp] - for use with charts
    """
    start_s = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")
    oneday = datetime.timedelta(days=1)
    day = start
    from django.db import connection
    from decimal import Decimal
    cursor = connection.cursor()
    sql = """
     SELECT ord.created::date, sum(ord.price)
     FROM orders_order ord 
     WHERE ord.created::date >= '%s' AND ord.created::date <= '%s'
     GROUP BY ord.created::date
    """ % (start_s, end_s)
    cursor.execute(sql)
    query_result = cursor.fetchall()
    result = []
    while day < end:
      q_day_data = [ q_result[1] for q_result in query_result if q_result[0] == day ]
      if len(q_day_data) > 0:
        result.append([self._make_js_timestamp(day), float(q_day_data[0])])
      else:
        result.append([self._make_js_timestamp(day), 0.0])
      day += oneday
    return result

  def order_amount_by_date(self, start=datetime.date.today()+datetime.timedelta(weeks=-1), end=datetime.date.today()):
    """
    Returns list of lists: [num_of_orders_for_day, js_timestamp] - for use with charts
    """
    start_s = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d")
    oneday = datetime.timedelta(days=1)
    day = start
    from django.db import connection
    from decimal import Decimal
    cursor = connection.cursor()
    sql = """
     SELECT ord.created::date, COUNT(*)
     FROM orders_order ord 
     WHERE ord.created::date >= '%s' AND ord.created::date <= '%s'
     GROUP BY ord.created::date
    """ % (start_s, end_s)
    cursor.execute(sql)
    query_result = cursor.fetchall()
    result = []
    while day < end:
      q_day_data = [ q_result[1] for q_result in query_result if q_result[0] == day ]
      if len(q_day_data) > 0:
        result.append([self._make_js_timestamp(day), q_day_data[0]])
      else:
        result.append([self._make_js_timestamp(day), 0])
      day += oneday
    return result

  def _make_js_timestamp(self, dt_object):    
    return calendar.timegm(dt_object.timetuple())*1000
