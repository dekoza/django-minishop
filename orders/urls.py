from django.conf.urls.defaults import *

urlpatterns = patterns('biolander.orders.views',
    url('^(?P<slug>[-\w]+)/add-to-cart/$', 'cart_add', name="add_to_cart"),
    url('^(?P<slug>[-\w]+)/remove-from-cart/$', 'cart_remove', name="remove_from_cart"),
    url('^koszyk/$', 'cart_show', name="show_cart"),
    url('^koszyk/oproznij/$', 'cart_flush', name="flush_cart"),
    url(r'^zamowienie/$', 'checkout', name="checkout"),
    url(r'^zamowienie/adres/(?P<type>shipping|billing)/$', 'address_change_type', name="checkout_change_address"),
    url(r'^zamowienie/zloz/$', 'place_order', name="place_order"),
    url('^ilosc/$', 'cart_quantity', name="cart_quantity"),
)
