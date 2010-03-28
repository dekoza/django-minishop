from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Category(models.Model):
  name = models.CharField(max_length=200, verbose_name=_("name"))
  slug = models.SlugField(verbose_name=_("slug"))
  description = models.TextField(null=True, blank=True, verbose_name=_("description"))

  class Meta:
    ordering = ('name',)
    verbose_name = _('category')
    verbose_name_plural = _('categories')
  def __unicode__(self):
      return self.name

class Post(models.Model):
  title = models.CharField(max_length=200, verbose_name=_("title"))
  slug = models.SlugField(verbose_name=_("slug"), unique=True)
  body = models.TextField(null=True, blank=True, verbose_name=_("body"))
  is_published = models.BooleanField(default=False, verbose_name=_("is published"))
  frontpage = models.BooleanField(default=False, verbose_name=_("frontpage"))
  categories = models.ManyToManyField(Category, verbose_name=_("categories"))
  created = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name=_("created"))
  modified = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name=_("modified"))

  class Meta:
    ordering = ('-created', '-title',)
    verbose_name = _('post')
    verbose_name_plural = _('posts')

  def __unicode__(self):
      return self.title
