from django.db import models
import random

# Create your models here.

class Generator(models.Manager):
  def make_vouchers(self, amount):
    v_ids = []
    for i in range(0, amount):
      try:
        new_v = Voucher(name="v", amount=5, code=self.random_string())
        new_v.save()
      except:
        new_v = Voucher(name="v", amount=5, code=self.random_string())
        new_v.save()
      v_ids.append(new_v.pk)
    return Voucher.objects.filter(pk__in=v_ids)

  def generate_single(self):
    try:
      new_v = Voucher(name="v1", amount=5, code=self.random_string())
      new_v.save()
    except:
      new_v = Voucher(name="v1", amount=5, code=self.random_string())
      new_v.save()
    return new_v      

  def random_string(self):
    string = ""
    rand_str = random.sample('abcdefghijklqmnopqrstuvwxyz0123456789',8)
    for i in rand_str:
      string += i
    return string

class Discount(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(null=True, blank=True)
  amount = models.DecimalField(max_digits=8, decimal_places=2)
  min_price = models.DecimalField(max_digits=8, decimal_places=2)
  max_price = models.DecimalField(max_digits=8, decimal_places=2)

class Voucher(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField(null=True, blank=True)
  amount = models.DecimalField(max_digits=8, decimal_places=2)
  code = models.CharField(max_length=200)

  objects = models.Manager()
  factory = Generator()
