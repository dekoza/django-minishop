# -*- coding: utf-8 -*-
from products.models import Product
from orders.utils import *
from orders.forms import *
from orders.models import *

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import list_detail
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from session_messages import create_message
from orders.cart import Cart
from django.utils.translation import ugettext_lazy as _
from customers.models import Address
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.core.mail import send_mail

# admin views ========================
@staff_member_required
def change_status(request, order_id):
  from orders.models import PAYMENT_STATUS as statuses
  if request.method == 'POST':
    status = int(request.POST['status'])
    #if status not in range(1, len(statuses)+1):
      #return conditional_redirect(request, '/admin/')
    order = Order.objects.get(pk=order_id)
    order.status = status
    if status == 5:
      items = order.ordereditem_set.all()
      for item in items:
        if (item.product.quantity - item.quantity) < 0:
          item.product.quantity = 0
        else:
          item.product.quantity = item.product.quantity - item.quantity
        item.product._order_cache = order
        print 'i.p',item.product
        item.product.save()
    order.save()
    #subject = render_to_string('customers/activation_email_subject.txt', { 'site': current_site })
    subject = u"Zmiana statusu zamówienia: %s" % order.get_status_type()
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    
    message = render_to_string('customers/status_change_email.txt',
                               { 'order': order,
                                 })
    from biolander import settings
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [order.user.email])
  return conditional_redirect(request, '/admin/')

@staff_member_required
def review_order(request, order_id):
  from orders.models import PAYMENT_STATUS as statuses
  order = Order.objects.get(pk=order_id)
  customer = order.user.get_profile()
  #shipping_address = customer.address_set.filter(is_shipping=True)[0]
  #billing_address = customer.address_set.filter(is_billing=True)[0]
  return render_to_response('admin/order_review.html', {
    'order':order,
    'statuses':statuses,
    'title':_("Order: %s" % order.name),
    'app_label': "Orders",
    #'shipping_address': shipping_address,
    #'billing_address': billing_address,
    'customer':customer
    }, context_instance=RequestContext(request)) 

@staff_member_required
def order_invoice(request, order_id, type='org'):
  from orders.invoice import Invoice
  order = get_object_or_404(Order, pk=order_id)
  invoice = Invoice(order, type)
  r = {'original':u"orginal", 'copy':u"kopia"}
  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'attachment; filename=faktura_09001'+str(order.pk)+'_'+r[type]+'.pdf'
  response.write(invoice.pdf())
  return response


@staff_member_required
def show_orders(request, type, page=1):
  from django.utils.datastructures import SortedDict
  app_labels = SortedDict([
      ('all', _("All orders")),
      ('new', _("New orders")),
      ('low_stock', _("Low on stock orders")),
      ('paid', _("Paid orders")),
      ('in_progress', _("Orders in progress")),
  ])
  query_types = {
      'all':Order.objects.all(),
      'new':Order.objects.filter(status=1),
      'low_stock':Order.stats.low_on_stock(),
      'paid':Order.objects.filter(status=4),
      'in_progress':Order.objects.filter(status=2),
      }
  app_label = title = app_labels[type]
  orders = query_types[type]
  count = orders.count()
  from orders.models import PAYMENT_STATUS as statuses
  return list_detail.object_list(
      request,
      queryset=orders,
      paginate_by=50,
      page=page,
      allow_empty=True,
      template_name='admin/order_list.html',
      extra_context={
        'app_types':app_labels,
        'app_label':app_label,
        'title':title,
        'statuses':statuses,
        'type':type,
        'count':count,
        })

def dotpay_reponse(request):
  transaction_name = request.POST.get('description', False)
  if transaction_name:
    order = Order.objects.get(name=transaction_name)
    from orders.dotpay import ProcessPayment
    payment = ProcessPayment(request, order)
    payment.set_order_status()
    return HttpResponse("OK")
  else:
    return HttpResponse("FAIL")
