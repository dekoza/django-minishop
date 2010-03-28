# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from orders.utils import log_change
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

TEST_SETTINGS = {
    'id': 00000,
    'currency': 'PLN',
    'lang': 'pl',
    'channel': None,
    'block': None,
    }
#DOTPAY_IPS = ['91.142.196.180']
DOTPAY_IPS = ['127.0.0.0']

class ProcessPayment(object):
  """
  Object to encapsulate dotpay payment gateway
  """
  def __init__(self, request, order):
    self.order = order
    self.request = request
    #print 'initialized ok'
    try:
      #from settings import DOTPAY, LANGUAGE_CODE, DOMAIN
      self.dotpay_settings = settings.DOTPAY
      self.language = settings.LANGUAGE_CODE
      self.domain = settings.DOMAIN
    except:
      self.dotpay_settings = TEST_SETTINGS
      self.language = 'pl_PL'
      self.domain = "biolander.pielgrzyma.com"

  def process(self):
    """
    Check payment type and run proper payment redirection
    """
    if self.order.payment_type == '3':
      return self._dotpay()
    else:
      return self._landing_page()

  def _dotpay(self):
    """
    Build GET data for dotpay.pl payment gateway and redirect
    """
    price = self.order.price
    if self.order.discount > 0:
      price = float(price) - float(self.order.discount)
    url = 'https://ssl.dotpay.pl/?id=%d&type=3' % self.dotpay_settings['id']
    url += "&description="+self.order.name
    url += "&amount=%f" % float(price)
    url += "&url=http://"+self.domain+reverse('landing_page')
    url += "&urlc=http://"+self.domain+reverse('dotpay_response')
    if not self.language == 'pl_PL':
      url += "&lang="+self.dotpay_settings['lang']
      url += "&currency"+self.dotpay_settings['currency']
    return HttpResponseRedirect(url)
    #return url

  def set_order_status(self):
    """
    Process payment callback from dotpay
    put it in logs and send shop staff email
    """
    status = self.request.POST.get('status', 'FAIL')
    t_status = self.request.POST.get('t_status',0)
    if self.request.META['REMOTE_ADDR'] not in DOTPAY_IPS:
      raise Http404
    if status == 'OK' and t_status == '2':
      self.order.status = 4
      log_change(self.request, self.order, "Recieved payment")
      self.order.save()
      subject = u"Zmiana statusu zamówienia: %s" % self.order.get_status_type()
      # Email subject *must not* contain newlines
      subject = ''.join(subject.splitlines())
      message = render_to_string('customers/status_change_email.txt',
                                 { 'order': self.order,
                                   })
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.order.user.email])
    elif t_status == '3':
      log_change(self.request, self.order, "Transaction aborted")
      self.order.status = 3
      self.order.save()

    staff_msg = render_to_string('email/admin_payment.txt', {
      'status': t_status,
      'order': self.order,
      })
    send_mail(u'Dotpay zmiana statusu zamówienia: %s' % self.order.name, staff_msg, settings.DEFAULT_FROM_EMAIL, settings.SHOP_STAFF_EMAILS)

  def _landing_page(self):
    """
    Redirect to landing page for transactions that don't need
    payment gateway
    """
    return render_to_response('orders/thankyou.html', context_instance=RequestContext(self.request))

