from django.db import models
from positions.fields import PositionField
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

# Create your models here.

class Slide(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("name"))
    image = models.ImageField(upload_to="slideshow", verbose_name=_("image"))
    link = models.URLField()
    text = models.TextField(verbose_name=_("text"))
    position = PositionField()

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        ordering = ('position', '-created', '-modified')
