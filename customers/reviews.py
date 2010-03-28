import csv
import datetime
from customers.models import *
from products.models import Product
from django.contrib.comments.models import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

class Reviews():
  def __init__(self, path):
    self.file = open(path)
    self.reader = csv.reader(self.file, delimiter=";")
    self.review_list = []
    self.orphans = []
    self.products = []
    #for line in self.reader:
      #self.review_list.append(line)
    self._populate_review_list()

  def _populate_review_list(self):
    for line in self.reader:
      try:
        prod = Product.objects.get(old_id=line[1])
        self.products.append(prod)
        self.review_list.append(line)
      except:
        self.orphans.append(line)

  def add_comments(self):
    #product_ct = ContentType.objects.get_for_model(Product)  
    site = Site.objects.get(pk=1)
    for i, line in enumerate(self.review_list):
      user = line[3]
      comment_txt = line[4]
      product = Product.objects.get(old_id=line[1])
      try:
        modified = datetime.datetime.strptime(line[5], "%Y-%m-%d %H:%M:%S")
      except:
        modified = datetime.datetime.today()
      comment = Comment(user_name=user, content_object=product, comment=comment_txt, submit_date=modified, site=site)
      comment.save() 
      print i, line[2], 'zapisany'
      #print comment.__dict__
