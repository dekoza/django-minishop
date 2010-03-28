# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer as Customer
from customers.models import Address as Address
from products.models import Product
from orders.stats import StatManager
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l
import datetime, calendar

# Create your models here.

PAYMENT_TYPES = (
    ('1', _("Pay using bank transfer")),
    ('2', _("Pay after shipment")),
    ('3', _("Online payment (dotpay.pl)")),
)

SHIPMENT_TYPES = (
    ('1', _("Normal package")),
    ('2', _("Priority package")),
    ('3', _("Courier")),
)

PAYMENT_STATUS = (
    (1, _("Pending")),
    (2, _("In progress")),
    (3, _("Rejected")),
    (4, _("Paid")),
    (5, _("Shipped")),
)
PAYMENT_STATUS_PL = (
    (1, u"Oczekujące"),
    (2, u"W realizacji"),
    (3, u"Odrzucone"),
    (4, u"Opłacone"),
    (5, u"Wysłane"),
)

class Order(models.Model):
    name = models.SlugField(unique=True, verbose_name=_("unique order name"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("price"))
    shipping_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("shipping price"))
    discount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("discount"))
    user = models.ForeignKey(User, verbose_name=_("user"))
    shipping_address = models.ForeignKey(Address, verbose_name=_("shipping address"), related_name='shipping_address')
    billing_address = models.ForeignKey(Address, verbose_name=_("billing address"), related_name='billing_address')
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPES, default=1, verbose_name=_("payment type"))
    shipment_type = models.PositiveIntegerField(choices=SHIPMENT_TYPES, default=1, verbose_name=_("shipment type"))
    status = models.PositiveIntegerField(choices=PAYMENT_STATUS, default=1, verbose_name=_("order status"))
    is_gift = models.BooleanField(default=False, verbose_name=_("is gift"))
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    objects = models.Manager()
    stats = StatManager()

    def get_shipment_type(self):
        if self.shipment_type is not None:
            return SHIPMENT_TYPES[self.shipment_type-1][1]

    def get_payment_type(self):
        if self.payment_type is not None:
            return PAYMENT_TYPES[self.payment_type-1][1]

    def get_status_type(self):
        if self.status is not None:
            return PAYMENT_STATUS_PL[self.status-1][1]

    def __unicode__(self):
        return self.name+" [ "+self.get_status_display()+" ]"

    def price_nett(self):
        """ Cena netto """
        return float(self.price)-self.price_tax()

    def price_tax(self):
        """ Wartość podatku (w zł) """
        return float(self.price)*0.18032786885

    def discounted_price(self):
        """ Cena brutto z uwzględnieniem rabatu """
        if self.discount:
            return self.price - self.discount
        else:
            return self.price

    def discounted_price_tax(self):
        if self.discount:
            return float(self.discounted_price())*0.18032786885
        else:
            return self.price_tax()

    def discounted_price_nett(self):
        """ Cena netto z uwzględnieniem rabatu """
        if self.discount:
            return float(self.discounted_price())-self.discounted_price_tax()
        else:
            return self.price_nett()

    def discount_nett(self):
        """ Zniżka netto """
        if float(self.discount) > 0:
            return float(self.discount)-self.discount_tax()
        else:
            return 0

    def discount_tax(self):
        """ Wartość podatku zniżki (w zł) """
        if float(self.discount) > 0:
            return float(self.discount)*0.18032786885
        else:
            return 0

    def shipping_price_nett(self):
        """ Cena dostawy netto """
        if float(self.shipping_price) > 0:
            return float(self.shipping_price)-self.shipping_price_tax()
        else:
            return 0

    def shipping_price_tax(self):
        """ Wartość podatku dla ceny dostawy """
        if float(self.shipping_price) > 0:
            return float(self.shipping_price)*0.18032786885
        else:
            return 0

    @property
    def invoice_number(self):
        return "09%05d" % (self.pk+100)

    class Meta:
        ordering = ('-created', 'name')

class OrderedItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"))
    user = models.ForeignKey(User, verbose_name=_("user"))
    product = models.ForeignKey(Product, verbose_name=_("product"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("price"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    quantity = models.PositiveIntegerField(verbose_name=_("quantity"))

    def get_price_total(self):
        return self.quantity*self.price

    def price_tax(self):
        return float(self.price)*0.18032786885

    def price_nett(self):
        return float(self.price)-self.price_tax()

    def price_total_tax(self):
        return float(self.price*self.quantity)*0.18032786885

    def price_total_nett(self):
        return float(self.price*self.quantity)-self.price_total_tax()

    def low_quantity(self):
        if self.id:
            if self.quantity >= self.product.quantity:
                return True
            else:
                return False
        else:
            return False

    def __unicode__(self):
        return self.description
