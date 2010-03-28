# -*- coding: utf-8 -*-
from products.models import Product
from orders.models import SHIPMENT_TYPES
from django.db import connection, models

# przedplata
SHIPMENT_RATES = [
   # [ waga, cena_id1, cena_id3 ]
   [1000, 9.5, 11],
   [2000, 11, 13],
   [5000, 13, 14.5],
   [5000, 13, 14.5],
   [10000, 18, 20.5],
   [15000, 21, 25],
   [20000, 30, 35],
   [30000, 36, 43],
    ]

# pobranie
SHIPMENT_RATES_2 = [ 
   # [ waga, cena_id1, cena_id3 ]
   [500, 10, 12],
   [1000, 13, 15],
   [2000, 15, 17],
   [5000, 17, 19],
   [10000, 25, 28],
    ]

# kurier
COURIER = 18

# minimalna kwota do darmowej wysyłki
FREE_SHIPPING = 200

class ShipmentError(Exception):
  pass

class Shipment():
  def __init__(self, cart):
    #if not isinstance(cart, Cart):
    #  raise ShipmentError()
    self.shipment_id = cart.shipment
    self.payment_id = cart.payment
    self.items = cart.items
    self.total_cost = cart.items_cost

    if self.payment_id == '2':
      self.rates = SHIPMENT_RATES_2
    else:
      self.rates = SHIPMENT_RATES

  def name(self):
    return SHIPMENT_TYPES[self.shipment_id+1]

  def total_weight(self):
    if len(self.items) > 0:
      items = ",".join(["("+str(i)+")" for i in self.items])
      query = """
      SELECT SUM(capacity) 
      FROM products_product
      JOIN (VALUES %s) AS v(id) ON (products_product.id = v.id)
      """ % items #% (Product.model._meta.db_table)
      cursor = connection.cursor()
      cursor.execute(query)#,[items])
      return cursor.fetchone()[0]
    else:
      return -1
      
  def cost(self):
    total_weight = self.total_weight()
    #return total_weight
    if total_weight > 0 and self.total_cost > FREE_SHIPPING:
      return 0
    if total_weight > 0 and not self.shipment_id == '3':
      for i, rate in enumerate(self.rates):
        if i == 0:
          if total_weight < rate[0]:
            return rate[int(self.shipment_id)]
        elif total_weight < rate[0]:
          return rate[int(self.shipment_id)]
        elif i == len(self.rates)-1 and total_weight > rate[0]:
          return rate[int(self.shipment_id)]
    elif total_weight > 0 and self.shipment_id == '3':
      return COURIER
    else:
      return -1
      
