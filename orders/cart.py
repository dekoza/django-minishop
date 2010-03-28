from products.models import Product
from orders.shipment import Shipment
from django.utils.translation import ugettext as _

class Cart():
  """
  Fat shopping cart object to encapsulate all cart functionality in a convenient wrapper.
  It doesn't store any data itself - instead fetches all the data from session. It requiers a 
  request instance as an init argument.

  _SESSION_TEMPLATE - list of cart variables. After init the keys are being cast to Cart instance's
  arguments for convenience of use. Do not change them unless you know what you are doing. You can add
  new keys for extra functionality.

  _PREFIX - prefix for each key in session
  """

  def __init__(self, request, **kwargs):
    """
    On init fetch session data and recalculate latest item if needed
    """
    self._SESSION_TEMPLATE = {
      'items':[],
      'items_cost':0, 
      'total_cost':0, 
      'latest_item': None, 
      'shipment': None, 
      'shipment_cost': 0, 
      'payment': None, 
      'shipping_address': None, 
      'billing_address': None, 
      }
    self._PREFIX = 'cart_'
    
    self.request = request
    self.session = request.session
    for key in self._SESSION_TEMPLATE:
      setattr(self, key, self.session.get(self._PREFIX+key, self._SESSION_TEMPLATE[key]))
    if not self.latest_item and len(self.items) > 0:
      self.latest_item = self._get_latest_item()


  def save(self):
    """
    Save cart instance's data to session
    """
    session_dict = {}
    for key in self._SESSION_TEMPLATE:
      self.session[self._PREFIX+key] = getattr(self, key)
  
  def _get_latest_item(self):
    """
    Fetch latest item's data from db as a dictionary
    """
    try:
      return Product.published.get(pk=self.items[-1]).__dict__
    except:
      return None

  def _calculate_quantities(self):
    """
    Returns a dictionary with item pk as key and item cart quantity as value
    """
    item_dict = {}
    for i in self.items:
      if item_dict.has_key(i):
        item_dict[i] += 1
      else:
        item_dict[i] = 1
    return item_dict

  def _calculate_items_cost(self):
    """
    Sets a total item cost excluding shipment/payment costs
    """
    price = 0
    try:
      items = Product.published.in_bulk(self.items)
      for item in self.items:
        price += items[item].price
      self.items_cost = price
      self.save()
    except:
      pass

  def refresh(self):
    """
    Refresh cart variables and save all session data
    """
    if len(self.items) > 0:
      self._calculate_items_cost()
    if self.latest_item:
      self.latest_item = self._get_latest_item()
    if self.shipment:
      shipment = Shipment(self)
      self.shipment_cost = shipment.cost()
    self.save()

  def add(self, item):
    """
    Add given item to cart. Accepts item.pk, Product objects or pk lists
    """
    if isinstance(item, int):
      self.items.append(item)
    elif isinstance(item, Product):
      self.items.append(item.pk)
    elif isinstance(item, list):
      self.items = self.items+item
    self.refresh()

  def remove(self, item):
    """
    Remove given item from cart (entirely). Accepts item.pk, Product objects or pk lists
    """
    if isinstance(item, int):
      self.items = [ i for i in self.items if i != item ]
    elif isinstance(item, Product):
      self.items = [ i for i in self.items if i != item.pk ]
    elif isinstance(item, list):
      for list_item in item:
        #TODO: zamiast != dac if not in list_item
        self.items = [ i for i in self.items if i != list_item ]
    self.refresh()

  def remove_oldest(self, item):
    """
    Remove oldest id of given item from cart. Accepts item.pk, Product objects or pk lists
    """
    if isinstance(item, int):
      self.items.remove(item)
    elif isinstance(item, Product):
      self.items.remove(item.pk)
    self.refresh()

  def flush(self):
    """
    Remove all items from cart and clear session data
    """
    for i in self.items:
      self.remove(i)
    for key in self._SESSION_TEMPLATE:
      setattr(self, key, self._SESSION_TEMPLATE[key])
    try:
      del self.request.session['voucher']
      del self.request.session['voucher_code']
    except:
      pass
    self.save()
    self.session[self._PREFIX+'items'] = []
    #self.refresh()
  
  def set_shipment(self, type):
    self.shipment = type
    shipment = Shipment(self)
    self.shipment_cost = shipment.cost()
    try:
      self.total_cost = float(self.items_cost) + float(self.shipment_cost)
    except:
      self.total_cost = 0
    self.refresh()

  def set_payment(self, type):
    self.payment = type
    self.refresh()


  def change_quantity(self, item, quantity):
    """
    Function for changing product quantity in cart
    """
    if isinstance(item, Product):
      product_pk = item.pk
    else:
      product_pk = item
    item_quantities = self._calculate_quantities()
    delta = item_quantities[product_pk] - quantity
    if not item_quantities[product_pk] == quantity and product_pk in self.items:
      if delta > 0:
        for i in range(delta):
          self.remove_oldest(product_pk)
      else:
        for i in range(-delta):
          self.items.insert(self.items.index(product_pk), product_pk)
      self.refresh()

  def full_list(self):
    """
    Provides a list of product objects + cart quantity + total price in cart for each
    """
    quantity_dict = self._calculate_quantities()
    product_dict = Product.published.filter(pk__in=self.items)
    for product in product_dict:
      product.cart_quantity = quantity_dict[product.pk]
      product.price_total = product.price*quantity_dict[product.pk]
    return product_dict

  def is_valid(self):
    """
    Validates shipping and payment methods
    """
    from session_messages import create_message
    if not self.shipment is None and not self.payment is None:
      from orders.models import PAYMENT_TYPES, SHIPMENT_TYPES
      if self.shipment in [m[0] for m in SHIPMENT_TYPES] and self.payment in [p[0] for p in PAYMENT_TYPES]:
        return True
      else:
        create_message(self.request, _("Invalid payment/shipment type. Please contact system administrator."), type=1)
        return False
    else:
      create_message(self.request, _("You have to choose payment and shipment method"), type=1)
      return False
