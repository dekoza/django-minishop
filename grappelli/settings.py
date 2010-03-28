# coding: utf-8

import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Admin Site Title
ADMIN_TITLE = getattr(settings, "GRAPPELLI_ADMIN_TITLE", _('biolander.com admin'))

# Admin Prefix
ADMIN_URL = getattr(settings, "GRAPPELLI_ADMIN_URL", 'admin')

