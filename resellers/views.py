from orders.utils import conditional_redirect
from resellers.forms import RegistrationForm
from resellers.models import Partner, PartnerHistory
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from session_messages import create_message
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
import simplejson as json
# Create your views here.

@login_required
def register(request):
    if request.user.get_profile().is_active_partner():
        return conditional_redirect(request, reverse('profile'))
    if request.method == 'GET':
        form = RegistrationForm(user=request.user)
    else:
        form = RegistrationForm(request.POST, user=request.user)
        if form.is_valid():
            partner = form.save(commit=False)
            partner.user = request.user
            partner.save()
            create_message(request, _("Registration successfull"))
            subject = "Nowy partner: %s %s" % (partner.user.first_name, partner.user.last_name)
            subject = ''.join(subject.splitlines())
            message = render_to_string('email/new_reseller.html', {
                'partner':partner
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.SHOP_STAFF_EMAILS)
            return conditional_redirect(request, reverse("profile"))
    return render_to_response(
        'resellers/registration.html', {
            'form':form,
            'next': request.REQUEST.get('next', ''),
        }, context_instance=RequestContext(request))

@login_required
def panel(request):
    if not request.user.get_profile().is_active_partner():
        create_message(request, _("You have not registered as partner or your account has not been aprooved"))
        return conditional_redirect(request, reverse('profile'))
    partner = Partner.objects.get(user=request.user)
    history = PartnerHistory.objects.income_daily(partner=partner)
    return render_to_response(
        'resellers/panel.html', {
            'partner':partner,
            'history':json.dumps(history),
            'next': request.REQUEST.get('next', ''),
        }, context_instance=RequestContext(request))
