from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import csv
import os
import time
from django.utils.encoding import force_unicode
from discounts.models import Voucher
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):

  def handle(self, *args, **options):
    file = open(args[0], 'rb') 
    csv_data = list(csv.reader(file))
    vouchers = Voucher.objects.all()
    for i, item in enumerate(csv_data):
      code = vouchers[i].code
      data = item[:4]
      data.append(code)

      sex = data[0]
      first_name = data[1]
      last_name = data[2]
      email = data[3]
      voucher = data[4]
      subject = 'Zapraszamy na zakupy w sklepie Biolander!'
      if i%20 == 0:
        print 'hrrr'
        time.sleep(30)
      message = render_to_string('email/welcome.txt', {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'sex': sex,
        'voucher': voucher,
        })
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
      print data
    file.close()
