# -*- coding: utf-8 -*-
from products.models import *
from products.forms import CategoryRecomendationsForm

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
import simplejson as json
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def ajax_get_recommendations(request, taxonomy_type):
    cat_id = request.GET.get('category_id', None)
    try:
        if taxonomy_type == 'category':
            Recommendation = CategoryRecommendation
        elif taxonomy_type == 'solution':
            Recommendation = SolutionRecommendation
        recommended = Recommendation.objects.filter(category__pk=cat_id)
        products = map(lambda x: {
            "pk": x.pk, 
            "position": x.position,
            "type": x.type,
            "product_id": x.product.pk,
            "name": x.product.name,
            "slug": x.product.slug,
                                 }, recommended)
    except:
        products = []
    return HttpResponse(json.dumps(products))

@staff_member_required
def ajax_get_products(request, taxonomy_type):
    cat_id = request.GET.get('category_id', None)
    try:
        if taxonomy_type == 'category':
            Taxonomy = Category
        elif taxonomy_type == 'solution':
            Taxonomy = Solution
        if int(cat_id) == 1:
            products = Product.published.all().order_by('name', 'price')
        else:
            products = Taxonomy.objects.get(pk=cat_id).product_set.all()
        products = map(lambda x: {
            "pk": x.pk, 
            "name": x.name,
            "price": float(x.price),
            #"slug": x.slug,
                                 }, products)
    except:
        products = []
    return HttpResponse(json.dumps(products))

@staff_member_required
def category_recommendations(request):
    if request.method == 'POST':
        pass
    else:
        form = CategoryRecomendationsForm()
        return render_to_response('admin/recommendations.html', {
            'form': form,
            'r_types': R_CHOICES,
        }, context_instance=RequestContext(request))

@staff_member_required
def save_recommendations(request, taxonomy_type):
    if taxonomy_type == 'category':
        Taxonomy = Category
        Recommendation = CategoryRecommendation
    elif taxonomy_type == 'solution':
        Taxonomy = Solution
        Recommendation = SolutionRecommendation

    # get data
    product_ids = request.GET.get('products', None)
    cat_id = request.GET.get('category_id', None)
    types = request.GET.get('types', None)
    if types:
        types = types.split(",")
    # validate if exists
    if not product_ids or not cat_id:
        return HttpResponse(json.dumps("ERROR"))
    # get category
    category = get_object_or_404(Taxonomy, pk=cat_id)
    existing_recom = Recommendation.objects.filter(category=category)

    # if no product ids
    if product_ids == 'removeall':
        existing_recom.delete()
        return HttpResponse(json.dumps("OK - category empty"))
    else:
        product_ids = product_ids.split(",")
    if len(types) != len(product_ids):
        return HttpResponse(json.dumps("ERROR"))
    # server flood protection
    old_products = map(lambda x: int(x), product_ids) == map(lambda x: x.product.pk, existing_recom)
    old_types = map(lambda x: int(x), types) == map(lambda x: x.type, existing_recom)
    print old_types
    if old_products and old_types:
        return HttpResponse(json.dumps("OK - no changes"))
    existing_recom_ids = set(map(lambda x: x.product.pk, existing_recom))
    #print 'old', existing_recom_ids, '\nnew', product_ids

    # now remove recommendations not present in product_ids
    ids_for_removal = existing_recom_ids-set(product_ids) # yay, nifty set operation!
    recom_for_removal = Recommendation.objects.filter(product__id__in=ids_for_removal, category=category)
    recom_for_removal.delete()

    # save new recommendation layout
    for i, pid in enumerate(product_ids):
        # if recommendation exists only modify it's position
        if pid in existing_recom_ids:
            #TODO: check for multiple recommendation exeptions
            r = filter(lambda x: x.product.pk == pid, existing_recom)
            r.position = i
            r.save()
        # add new recommendation
        else:
            r_product = Product.objects.get(pk=pid)
            new_r = Recommendation(product=r_product, type=types[i], category=category,
                                   position=i)
            new_r.save()
    return HttpResponse(json.dumps("OK"))

