# -*- coding: utf-8 -*-
from products.models import Product
from orders.utils import *
from orders.forms import *
from orders.models import *
from discounts.code import CodeValidator

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import list_detail
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from session_messages import create_message
from orders.cart import Cart
from django.utils.translation import ugettext as _
from customers.models import Address
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import datetime

ORDER_TIME_DELTA = getattr(settings, 'ORDER_TIME_DELTA', 30)

def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity = request.GET.get('quantity', False)
    cart = Cart(request)
    if quantity:
        cart.add([product.pk for i in range(0, int(quantity))])
    else:
        cart.add(product)
    create_message(request, _("Product %s added") % product.name)
    return conditional_redirect(request, reverse('show_cart'))

def cart_remove(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = Cart(request)
    cart.remove(product)
    return conditional_redirect(request, reverse('show_cart'))

def cart_quantity(request):
    """
    Change given item's quantity in shopping cart.
    """
    if request.method == 'POST':
        try:
            product_slug = request.POST.get('slug', False)
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                product = Product.published.get(slug=product_slug)
                cart = Cart(request)
                cart.change_quantity(product, quantity)
        except:
            pass
    return conditional_redirect(request, reverse('show_cart'))

def cart_flush(request):
    """
    Remove all items from cart and flush session data related to cart.
    """
    cart = Cart(request)
    cart.flush()
    create_message(request, _("Cart has been flushed"))
    return conditional_redirect(request, '/')

def cart_show(request):
    cart = Cart(request)
    if request.method == 'POST':
        payment_shipment = PaymentShipment(request.POST)
    else:
        payment = cart.payment
        shipment = cart.shipment
        if payment and shipment:
            payment_shipment = PaymentShipment({'payment':payment, 'shipment':shipment})
        else:
            payment_shipment = PaymentShipment()


    if payment_shipment.is_valid():
        valid_payment = payment_shipment.cleaned_data['payment']
        valid_shipment = payment_shipment.cleaned_data['shipment']
        cart.set_payment(valid_payment)
        cart.set_shipment(valid_shipment)
        
    return render_to_response('orders/show_cart.html', {
        'object_list': cart.full_list(),
        'payment_shipment': payment_shipment,
        'shipment_price': cart.shipment_cost,
        'total_cost': cart.total_cost,
        }, context_instance=RequestContext(request))

@login_required
def checkout(request):
    cart = Cart(request)
    discount = CodeValidator(request, cart)
    if not cart.is_valid():
        return conditional_redirect(request, reverse('show_cart'))
    
    if request.method == 'POST':
        try:
            if request.POST['type'] == 'billing':
                cart.billing_address = request.POST['address']
                cart.refresh()
            elif request.POST['type'] == 'shipping':
                cart.shipping_address = request.POST['address']
                cart.refresh()
        except:
            pass

    if cart.shipping_address is not None:
        shipping_addr = Address.published.get(pk=cart.shipping_address)
        if shipping_addr.customer != request.user.get_profile():
            cart.flush()
            return conditional_redirect(request, '/')
    else:
        shipping_addr = request.user.get_profile().shipping_address()
        #shipping_addr = Address.published.get(customer=request.user.get_profile(), is_shipping=True)

    if cart.billing_address is not None:
        billing_addr = Address.published.get(pk=cart.billing_address)
        if billing_addr.customer != request.user.get_profile():
            cart.flush()
            return conditional_redirect(request, '/')
    else:
        billing_addr = request.user.get_profile().billing_address()
        #billing_addr = Address.published.get(Q(customer=request.user.get_profile()), Q(is_billing=True) | Q(is_shipping=True))

    return render_to_response('orders/checkout.html', {
        'object_list': cart.full_list(),
        'shipping_address': shipping_addr,
        'billing_address': billing_addr,
        'discount': discount,
        }, context_instance=RequestContext(request))


@login_required
def address_change_type(request, type):
    if request.method == 'GET':
        addresses = Address.published.filter(customer=request.user.get_profile())
        return render_to_response('customers/profile_address_type.html', {'addresses':addresses, 'type':type }, context_instance=RequestContext(request)) 

@login_required
def place_order(request):
    if request.method == 'POST':
        cart = Cart(request)
        discount = CodeValidator(request, cart)
        prev_orders_count = Order.objects.filter(user=request.user).count()
        if not cart.is_valid():
            return conditional_redirect(request, reverse('show_cart'))
        customer = request.user.get_profile()
        if not customer.shipping_address():
            create_message(request, _("You haven't chosen shipping address."))
            return conditional_redirect(request, reverse('profile_address'))
    else:
        return conditional_redirect(request, reverse('show_cart'))

    if cart.shipping_address is not None:
        shipping_addr = Address.published.get(pk=cart.shipping_address)
    else:
        shipping_addr = request.user.get_profile().shipping_address()
        #shipping_addr = Address.published.get(customer=request.user.get_profile(), is_shipping=True)

    if cart.billing_address is not None:
        billing_addr = Address.published.get(pk=cart.billing_address)
    else:
        billing_addr = request.user.get_profile().billing_address()
        #billing_addr = Address.published.get(Q(customer=request.user.get_profile()), Q(is_billing=True) | Q(is_shipping=True))

    now = datetime.datetime.now()
    try:
        last_order = Order.objects.filter(user=request.user)[-1]
    except:
        last_order = None
    if last_order:
        diff = now - last_order.created
        if diff.seconds <= ORDER_TIME_DELTA:
            create_message(request, _("Your order has already been filled"))
            return conditional_redirect(request, '/')

    new_order = Order(name = str(request.user.email)+"-"+str(prev_orders_count),
            price = str(cart.total_cost), discount = str(discount.calculated_amount), user=request.user, shipping_price = str(cart.shipment_cost),
            shipping_address=shipping_addr, billing_address=billing_addr,
            payment_type=str(cart.payment), shipment_type=cart.shipment, is_gift = False)
    new_order.save()

    if discount.partner and discount.partner.is_active:
        from resellers.utils import log_order
        log_order(discount.partner, new_order)

    discount.kill()

    for item in cart.full_list():
        ordered_item = OrderedItem(order=new_order, user=request.user, product=item, price=item.price, quantity=item.cart_quantity, description=item.name)
        ordered_item.save()
    payment = cart.payment
    order_name = str(request.user.email)+"-"+str(prev_orders_count)
    cart.flush()
    # email notification
    subject = "Biolander otrzymał Twoje zamówienie!"
    #subject = _("New order: %s" % new_order.name)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email_billing = new_order.billing_address
    email_shipping = new_order.shipping_address
    message = render_to_string('email/place_order.html', {
        'order': new_order,
        'billing': email_billing,
        'shipping': email_shipping,
        })
    staff_msg = render_to_string('email/admin_new_order.html', {
        'order': new_order,
        'billing': email_billing,
        'shipping': email_shipping,
        })

    from django.conf import settings
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_order.user.email])
    send_mail('Nowe zamówienie: %s' % new_order.name, staff_msg, settings.DEFAULT_FROM_EMAIL, settings.SHOP_STAFF_EMAILS)
    # has to be here to avoid circular dependencies
    from orders.dotpay import ProcessPayment
    payment = ProcessPayment(request, new_order)
    return payment.process()
