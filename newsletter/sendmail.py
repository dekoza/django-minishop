from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from discounts.models import Voucher
import time
import re
from django.contrib.auth.models import User

class Sendmail():
  template = 'email/welcome.txt'
  subject = 'Test email'

  def __init__(self, recipients, subject=None, template=None):
    self.recipients = recipients
    if template:
      self.template = template
    if subject:
      self.subject = subject
  def _get_subject(self):
    return ''.join(self.subject.splitlines())

  def _fetch_registered_emails(self):
    users = User.objects.all()
    emails = []
    for u in users:
      if u.email:
        emails.append(u.email)
    return emails

  def _send_mail(self, data):
    sex = data[0]
    first_name = data[1]
    last_name = data[2]
    email = data[3]
    voucher = Voucher.factory.generate_single()
    subject = self._get_subject()
    message = render_to_string(self.template, {
      'first_name': first_name,
      'last_name': last_name,
      'email': email,
      'sex': sex,
      'voucher': voucher,
      })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

  def send(self, delay=None, range=None):
    if not range is None:
      recipients = self.recipients[range[0]:range[1]]
    else:
      recipients = self.recipients

    for r in recipients:
      if delay:
        time.sleep(delay)
      self._send_mail(r)
      print r[1],r[2],"-",r[3]

  def send_to_unregistered(self, delay=None, range=None):
    if not range is None:
      recipients = self.recipients[range[0]:range[1]]
    else:
      recipients = self.recipients

    userbase = self._fetch_registered_emails()

    for r in recipients:
      if delay:
        time.sleep(delay)
      if not r[3] in userbase:
        self._send_mail(r)
        print r[1],r[2],"-",r[3]
      else:
        print 'OMITTED-REGISTERED-USER', r[1],r[2],"-",r[3]

  def dummy(self, delay=None, range=None):
    if not range is None:
      recipients = self.recipients[range[0]:range[1]]
    else:
      recipients = self.recipients

    for r in recipients:
      if delay:
        time.sleep(delay)
      print r[1],r[2],"-",r[3]

  def test_unregistered(self):
    recipients = self.recipients

    userbase = self._fetch_registered_emails()
    for r in recipients:
      if r[3] in userbase:
        print r[3]
  
  def test(self):
    email_re = re.compile(
      r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
      r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
      r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain
    failed = [] 
    for i, r in enumerate(self.recipients):
      if not email_re.search(r[3]):
        failed.append(i+1) 
    return failed

  def list_customers(self):
    customers = []
    for r in self.recipients:
      users = User.objects.filter(email=r[3])
      if len(users):
        print users
        customers += [u.pk for u in users ]
    return customers
