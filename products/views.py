# -*- coding: utf-8 -*-
from products.models import *

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.utils import translation
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import list_detail
from django.db.models import Q
from orders.utils import conditional_redirect
from session_messages import create_message
from django.conf import settings

PRODUCTS_PER_PAGE = getattr(settings, "PRODUCTS_PER_PAGE", 12)

def show_category(request, slug, page=1):
  category = get_object_or_404(Category, slug=slug)
  subcategories = category.get_descendants(include_self=True)
  products = Product.published.filter(categories__in=subcategories).distinct()
  print 'pr', len(products)
  if len(category.recommended):
      products = products.exclude(pk__in=[r.pk for r in category.recommended])
  print 'pr', len(products)
  template = 'products/product_list.html'
  return list_detail.object_list(
      request,
      queryset=products,
      paginate_by=PRODUCTS_PER_PAGE,
      page=page,
      allow_empty=True,
      template_name=template,
      extra_context={'category':category, 'subcategories':subcategories})

def show_solution(request, slug, page=1):
  solution = get_object_or_404(Solution, slug=slug)
  subsolutions = solution.get_descendants(include_self=True)
  products = Product.published.filter(solutions__in=subsolutions).distinct()
  template = 'products/product_list_solutions.html'
  return list_detail.object_list(
      request,
      queryset=products,
      paginate_by=PRODUCTS_PER_PAGE,
      page=page,
      allow_empty=True,
      template_name=template,
      extra_context={'category':solution, 'subcategories':subsolutions})

def manufacturer_list(request):
  manufacturers = Manufacturer.objects.all()
  template = 'products/manufacturers.html'
  return list_detail.object_list(
      request,
      queryset=manufacturers,
      allow_empty=True,
      template_name=template)

def show_manufacturer(request, slug, page=1):
  manufacturer = get_object_or_404(Manufacturer, slug=slug)
  products = Product.published.filter(manufacturer=manufacturer).distinct()
  template = 'products/product_list_manufacturers.html'
  return list_detail.object_list(
      request,
      queryset=products,
      paginate_by=PRODUCTS_PER_PAGE,
      page=page,
      allow_empty=True,
      template_name=template,
      extra_context={'category':manufacturer})

def show_manufacturer_product(request, manufacturer_slug, slug):
  manufacturer = get_object_or_404(Manufacturer, slug=manufacturer_slug)
  products = Product.published.all()
  template = 'products/product_detail_manufacturer.html'
  return list_detail.object_detail(
      request,
      queryset=products,
      slug=slug,
      slug_field='slug',
      template_name=template,
      extra_context={'manufacturer':manufacturer})
  
def show_category_product(request, category_slug, slug):
  category = get_object_or_404(Category, slug=category_slug)
  products = Product.published.all()
  template = 'products/product_detail.html'
  return list_detail.object_detail(
      request,
      queryset=products,
      slug=slug,
      slug_field='slug',
      template_name=template,
      extra_context={'category':category})

def show_solution_product(request, solution_slug, slug):
  category = get_object_or_404(Solution, slug=solution_slug)
  products = Product.published.all()
  template = 'products/product_detail_solution.html'
  return list_detail.object_detail(
      request,
      queryset=products,
      slug=slug,
      slug_field='slug',
      template_name=template,
      extra_context={'category':category})

def search(request, page=1):
  if request.method == 'GET':
    q = request.GET.get('q', "").strip()
    if len(q) < 3:
      create_message(request, "Fraza zbyt któtka")
      return conditional_redirect(request, '/')
    products = Product.published.filter(
      Q(name__icontains = q) |
      Q(description__icontains = q) |
      Q(usage__icontains = q) |
      Q(ingredients__icontains = q) 
        )
  else:
    return conditional_redirect(request, '/')
  template = 'products/product_search.html'
  return list_detail.object_list(
      request,
      queryset=products,
      paginate_by=PRODUCTS_PER_PAGE,
      page=page,
      allow_empty=True,
      template_name=template,
      extra_context={'phrase':q})


#TODO: dostep tylko dla staffu
def tree_list(request, model):
  tree_model = None
  model_name = None
  if model == 'categories':
    tree_model = 'Categories'
    model_name = 'Categories'
    model_name_singular = 'Category'
  elif model == 'solutions':
    tree_model = Solution
    model_name = 'Solutions'
    model_name_singular = 'Solution'
  return render_to_response('admin/tree_list.html', {
    'tree_model': tree_model,
    'model_name': model_name,
    'model_name_singular': model_name_singular,
    }, context_instance=RequestContext(request))

