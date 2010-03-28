from customers.forms import *
from customers.models import Address, Customer, LastAddress
from orders.utils import conditional_redirect
from orders.models import Order, OrderedItem
from orders.cart import Cart

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import list_detail
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from session_messages import create_message
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib.auth.forms import PasswordResetForm

import base64
# Create your views here.

def activate(request, activation_key):
  activation_key = activation_key.lower() # Normalize before trying anything with it.
  account = Customer.objects.activate_user(activation_key)
  create_message(request, _("Activation successfull"))
  return conditional_redirect(request, reverse('login'))
  

def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST) 
    accept = RegistrationConfirmForm(request.POST)
    formset = AddressFormset(request.POST)
    formset.forms[0].empty_permitted = False
    formset.forms[1].empty_permitted = True
    if form.is_valid() and accept.is_valid() and formset.is_valid():
      new_user = form.save() # all the additional user data saved here
      new_customer = new_user.get_profile()

      #new_customer.type = form.cleaned_data['type']
      new_customer.birthdate = form.cleaned_data['birthdate']
      #new_customer.company_name = form.cleaned_data['company_name']
      #new_customer.nip = form.cleaned_data['nip']
      #new_customer.newsletter = accept.cleaned_data['accept_newsletter']
      new_customer.save()

      #addresses = formset.save(commit=False)
      for i, address in enumerate(formset.forms):
        if address.has_changed():
          address = address.save(commit=False)
          address.customer = new_customer
          if i == 0:
            address.is_billing = True
          elif i == 1:
            address.is_shipping = True
          address.save()

      return render_to_response('customers/registration_complete.html', {
        'registered_user': new_user,
        'next': request.REQUEST.get('next', ''),
        }, context_instance=RequestContext(request)) 
    else:
      return render_to_response('customers/registration.html', { 
        'form':form,
        'next': request.REQUEST.get('next', ''),
        'formset':formset,
        'accept':accept,
        }, context_instance=RequestContext(request))
  else:
    form = RegistrationForm() 
    accept = RegistrationConfirmForm()
    formset = AddressFormset()
    formset.forms[0].empty_permitted = False
    formset.forms[1].empty_permitted = True
    return render_to_response('customers/registration.html', { 
      'form':form,
      'next': request.REQUEST.get('next', ''),
      'formset':formset,
      'accept':accept,
      }, context_instance=RequestContext(request))

def login_user(request):
  password_form = PasswordResetForm()
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse('logout'))
  if request.method == 'POST':
    login_form = LoginForm(data=request.POST)
    if login_form.is_valid():
      login(request, login_form.get_user())
      request.session.set_expiry(1800)
      return conditional_redirect(request, reverse('profile'))
    else:
      # invalid login form
      create_message(request, _("Due to recent complex changes in our shop you have to register even if you've had an account in old biolander"), type=1)
      return render_to_response('customers/login.html', {'form':login_form, 'password_form':password_form}, context_instance=RequestContext(request)) 
  else:
    # empty form
    login_form = LoginForm()
    return render_to_response('customers/login.html', {'form':login_form, 'password_form':password_form, 'next':request.GET.get('next', '')}, context_instance=RequestContext(request)) 

@login_required
def logout_user(request):
  request.session['new_cart'] = None
  cart = Cart(request)
  cart.flush()
  logout(request)
  return render_to_response('customers/logout.html', context_instance=RequestContext(request)) 

@login_required
def profile(request):
  order_history = Order.objects.filter(user=request.user)
  return render_to_response('customers/profile_order_history.html', {'order_history':order_history }, context_instance=RequestContext(request)) 

@login_required
def profile_edit(request):
  if request.method == 'POST' and not request.user.is_staff:
    profile_form = ProfileChangeForm(request.POST)
    if profile_form.is_valid():
      email = profile_form.cleaned_data['email']
      first_name = profile_form.cleaned_data['first_name']
      last_name = profile_form.cleaned_data['last_name']
      username = base64.b64encode(email)[:30]
      user = User.objects.get(username=request.user.username)
      user.first_name = first_name
      user.last_name = last_name
      user.email = email
      user.username = username
      user.save()
      create_message(request, _("Operation successfull"))
  else:
    profile_form = ProfileChangeForm(instance=request.user)
  return render_to_response('customers/profile_edit.html', {'profile_form':profile_form }, context_instance=RequestContext(request)) 

@login_required
def password_change(request):
  if request.method == 'POST' and not request.user.is_staff:
    password_form = PasswordChangeForm(user=request.user, data=request.POST)
    if password_form.is_valid():
      password_form.save()
      password_form = PasswordChangeForm(user=request.user)
      create_message(request, _("Password change successfull"))
  else:
    password_form = PasswordChangeForm(user=request.user)
  return render_to_response('customers/profile_password.html', {'password_form':password_form }, context_instance=RequestContext(request)) 

@login_required
def profile_history(request):
  pass

@login_required
def address_list(request, page=1):
  try:
    address = Address.published.filter(customer=request.user.get_profile())
  except Customer.DoesNotExist:
    return conditional_redirect(request, reverse('profile'))
  except:
    raise Http404
  return list_detail.object_list(
      request,
      queryset=address,
      paginate_by=6,
      page=page,
      allow_empty=True,
      extra_context={'user':request.user})

@login_required
def address_edit(request, address_id):
  address = Address.published.get(pk=address_id)
  if not address.customer == request.user.get_profile():
    raise Http404
  if request.method == 'POST' and not request.user.is_staff:
    form = AddressEditForm(request.POST, instance=address)
    if form.is_valid():
      form.save()
      create_message(request, _("Operation successfull"))
      return conditional_redirect(request, reverse('profile_address'))
  else:
    form = AddressEditForm(instance=address)
  return render_to_response('customers/profile_address_add.html', {'form':form }, context_instance=RequestContext(request)) 

@login_required
def address_add(request):
  next = request.REQUEST.get('next', False)
  if request.method == 'POST' and not request.user.is_staff:
    form = AddressEditForm(request.POST)
    if form.is_valid():
      address = form.save(commit=False)
      customer = request.user.get_profile()
      address.customer = customer
      address.save()
      create_message(request, _("Operation successfull"))
      return conditional_redirect(request, reverse('profile_address'))
  else:
    form = AddressEditForm()
  return render_to_response('customers/profile_address_add.html', {'form':form, 'next':next }, context_instance=RequestContext(request)) 

@login_required
def address_delete(request, address_id):
  address = Address.published.get(pk=address_id)
  if not address.customer == request.user.get_profile() or request.user.is_staff:
    raise Http404
  try:
    address.delete()
    #create_message(request, "Address successfully deleted")
    create_message(request, _("Address successfully deleted"))
  except: 
    create_message(request, _("You cannot delete all your addresses"))
  return conditional_redirect(request, reverse('profile_address'))

@login_required
def favorites(request):
  pass
