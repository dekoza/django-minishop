from django.db import models
from datetime import datetime
import mptt
from imaging.fields import ImagingField
from imaging.models import Image
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from products.stock_management import StockManager, stock_logger
from django.db.models.signals import pre_save
from positions.fields import PositionField

class PublishedManager(models.Manager):
  def get_query_set(self):
    return super(PublishedManager, self).get_query_set().filter(is_published=True)


class Manufacturer(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(unique=True, verbose_name=_("slug"))
  logo = models.ImageField(upload_to="manufacturer_logos", null=True, blank=True, verbose_name=_("logo"))

  description = models.TextField(null=True, blank=True, verbose_name=_("description"))

  class Meta:
    verbose_name = _('manufacturer')
    verbose_name_plural = _('manufacturers')
    ordering = ('name',)

  def get_absolute_url(self):
    return "/manufacturer/%s/" % self.slug
  def __unicode__(self):
      return self.name

  def get_logo(self):
    if self.logo:
      return self.logo.url
    else:
      return '/media/manufacturer_logos/default.png'

class Solution(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(unique=True, verbose_name=_("slug"))
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_("parent"))

  description = models.TextField(null=True, blank=True, verbose_name=_("description"))
  _recomended = models.ManyToManyField('Product', through='SolutionRecommendation')
  @property
  def recommended(self):
    return self._recomended.order_by('solutionrecommendation__position')
  created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
  modified = models.DateTimeField(null=True, blank=True, auto_now=True)

  def __unicode__(self):
      return self.name
  class Meta:
    ordering = ('-created', '-modified')
    verbose_name = _('solution')
    verbose_name_plural = _('solutions')

class Category(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(unique=True, verbose_name=_("slug"))
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_("parent"))
  is_main = models.BooleanField(default=False)
  old_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Old id"))
  image = models.ImageField(upload_to="category_images", verbose_name=_("logo"), null=True, blank=True)
  _recomended = models.ManyToManyField('Product', through='CategoryRecommendation')
  @property
  def recommended(self):
    return self._recomended.order_by('categoryrecommendation__position')

  def get_image(self):
    if self.image:
      return self.image.url
    else:
      return '/media/category_images/default.png'

  description = models.TextField(null=True, blank=True, verbose_name=_("description"))

  created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
  modified = models.DateTimeField(null=True, blank=True, auto_now=True)

  def __unicode__(self):
      return self.name
  class Meta:
    ordering = ('-created', '-modified')
    verbose_name = _('category')
    verbose_name_plural = _('categories')

try:
  mptt.register(Category, order_insertion_by=['slug'])
  mptt.register(Solution, order_insertion_by=['slug'])
except mptt.AlreadyRegistered:
  pass

class Certificate(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(unique=True, verbose_name=_("slug"))
  logo = models.ImageField(upload_to="certificate_logos", verbose_name=_("logo"))

  description = models.TextField(null=True, blank=True, verbose_name=_("description"))

  class Meta:
    verbose_name = _('certificate')
    verbose_name_plural = _('certificates')

  def get_absolute_url(self):
    return "/certificate/%s/" % self.slug
  def __unicode__(self):
      return self.name

CAPACITY_TYPES = (
    ('0', _('g')),
    ('1', _('ml')),
)

AVAILIBILITY_TYPES = (
    ('0', _('24h')),
    ('1', _('3 days')),
    ('2', _('week')),
    ('3', _('not availible')),
)

class Product(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(unique=True, verbose_name=_("slug"))
  catalogue_number = models.CharField(max_length=200, verbose_name=_("catalogue number"))
  price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("price"))
  wholesale_price = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2, verbose_name=_("wholesale price"))
  old_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_("Old id"))

  capacity = models.PositiveIntegerField(verbose_name=_("capacity"))
  capacity_type = models.PositiveIntegerField(choices=CAPACITY_TYPES, default=0, verbose_name=_("capacity type"))
  def show_capacity_type(self):
    try:
      return CAPACITY_TYPES[self.capacity_type][1]
    except:
      return _("unknown")

  availibility = models.PositiveIntegerField(choices=AVAILIBILITY_TYPES, default=0, verbose_name=_("availibility"))
  def show_availibility(self):
    try:
      if self.quantity > 0:
        return AVAILIBILITY_TYPES[self.availibility][1]
      else:
        return AVAILIBILITY_TYPES['3'][1]
    except:
      return _("unknown")

  quantity = models.PositiveIntegerField(verbose_name=_("quantity"))

  is_published = models.BooleanField(default=True, verbose_name=_("is published"))
  is_gift = models.BooleanField(default=False, verbose_name=_("is gift"))

  photos = ImagingField(null=True, blank=True, verbose_name=_("product photos"))
  photos_set = generic.GenericRelation(Image)

  manufacturer = models.ForeignKey(Manufacturer, verbose_name=_("manufacturer"))
  certificates = models.ManyToManyField(Certificate, null=True, blank=True, verbose_name=_("certificates"))
  categories = models.ManyToManyField(Category, verbose_name=_("categories"))
  solutions = models.ManyToManyField(Solution, null=True, blank=True, verbose_name=_("solutions"))

  description = models.TextField(null=True, blank=True, verbose_name=_("description"))
  usage = models.TextField(null=True, blank=True, verbose_name=_("usage"))
  ingredients = models.TextField(null=True, blank=True, verbose_name=_("ingredients"))

  created = models.DateTimeField(null=True, blank=True, default=datetime.now)
  modified = models.DateTimeField(null=True, blank=True, auto_now=True)

  objects = models.Manager()
  published = PublishedManager()
  stock = StockManager()

  def price_with_tax(self):
    if self.price:
      return self.price + (self.price*22/100)

  def tax(self):
    if self.price:
      return self.price*22/100

  def product_thumbnail(self):
    if len(self.photos_set.all()) > 0:
      try:
        photo = self.photos_set.get(ordering=0)
      except self.MultipleObjectsReturned:
        photo = self.photos_set.filter(ordering=0)[0]
      except:
        return None
      thb_url = photo.get_small_thumb_url()
      return mark_safe('<img src="'+thb_url+'" />')
    else:
      return  mark_safe(' ')
  product_thumbnail.allow_tags = True
  
  def get_votes(self):
    from voting.models import Vote
    vote_array = [0,0,0,0,0]
    try:
      votes = Vote.objects.get_score(self)
      for i in range(0, votes['score']):
        vote_array[i] = 1
    except:
      pass
    return vote_array

  def volume(self):
    return self.quantity*self.price

  def wholesale_volume(self):
      if self.wholesale_price:
          return self.quantity*self.wholesale_price
      else:
          return 0

  def __unicode__(self):
      return self.name

  class Meta:
    verbose_name = _('product')
    verbose_name_plural = _('products')
    ordering = ('-created', '-modified')


pre_save.connect(stock_logger, sender=Product)

R_CHOICES = (
    (0, _("Normal")),
    (1, _("New")),
    (2, _("Recommended")),
    )

class RecommendationBase(models.Model):
  class Meta:
    abstract = True

  product = models.ForeignKey(Product)
  type = models.IntegerField(choices=R_CHOICES) 
  created = models.DateTimeField(null=True, blank=True, default=datetime.now)
  modified = models.DateTimeField(null=True, blank=True, auto_now=True)

class CategoryRecommendation(RecommendationBase):
  category = models.ForeignKey(Category)
  position = PositionField(unique_for_field='category')

  class Meta:
    verbose_name = _('recommended for category')
    verbose_name_plural = _('recommended for category')
    ordering = ('position', '-created', '-modified')

class SolutionRecommendation(RecommendationBase):
  category = models.ForeignKey(Solution)
  position = PositionField(unique_for_field='category')

  class Meta:
    verbose_name = _('recommended for solution')
    verbose_name_plural = _('recommended for solution')
    ordering = ('position', '-created', '-modified')
