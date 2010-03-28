from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from orders.dotpay import DOTPAY_IPS

class OrdersTest(TestCase):
  fixtures = [
      'manufacturers.json',
      'solutions.json',
      'categories.json',
      'certificates.json',
      'products.json',
      'users.json',
      'customers.json',
      'orders.json'
      ]

  def test_dotpay_ip_check(self):
    data = {
      'status' : 'OK',
      't_status': '2',
      'description':'test@test.com-0',
        }
    response = self.client.post(reverse("dotpay_response"), data, REMOTE_ADDR='127.0.0.1')
    self.assertEquals(response.status_code, 404)

  def test_dotpay_callback_positive(self):
    data = {
      'status' : 'OK',
      't_status': '2',
      'description':'test@test.com-0',
        }
    response = self.client.post(reverse("dotpay_response"), data, REMOTE_ADDR=DOTPAY_IPS[0])
    self.assertEquals(len(mail.outbox), 2)
    self.assertContains(response, 'OK', status_code=200)

  def test_dotpay_callback_negative(self):
    data = {
      'status' : 'OK',
      't_status': '3',
      'description':'test@test.com-0',
        }
    response = self.client.post(reverse("dotpay_response"), data, REMOTE_ADDR=DOTPAY_IPS[0])
    self.assertEquals(len(mail.outbox), 1)
    self.assertContains(response, 'OK', status_code=200)

