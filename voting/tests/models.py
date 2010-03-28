from django.db import models

class Item(models.Model):
    name = models.CharField(maxlength=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
