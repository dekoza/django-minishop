from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models

# Generic relations were moved in Django revision 5172
try:
    from django.contrib.contenttypes import generic
except ImportError:
    import django.db.models as generic

from voting import settings
from voting.managers import VoteManager

class Vote(models.Model):
    """
    A vote on an object by a User.
    """
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type', 'object_id')
    vote = models.SmallIntegerField(choices=settings.SCORES)

    objects = VoteManager()

    class Meta:
        db_table = 'votes'
        # Enforce one vote per user per object
        unique_together = (('user', 'content_type', 'object_id'),)

    class Admin:
        pass

    def __unicode__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.object)
