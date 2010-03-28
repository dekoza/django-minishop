# -*- coding: utf-8 -*-
from resellers.models import *

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from session_messages import create_message
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from orders.utils import conditional_redirect

@staff_member_required
def display_partner(request, object_id):
    partner = get_object_or_404(Partner, pk=object_id)
    return render_to_response('admin/partner_display.html', {
        'partner':partner,
        'title':_("Partner: %s" % partner.full_name),
        'app_label': "Resellers",
    }, context_instance=RequestContext(request)) 

@staff_member_required
def toggle_activation(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id)
    if partner.is_active:
        partner.is_active = False
    else:
        partner.is_active = True
    partner.save()
    return conditional_redirect(request, "/panel/resellers/partner/%d/" % partner.pk)
