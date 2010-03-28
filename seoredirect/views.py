from products.models import *
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponse
from django.core.urlresolvers import reverse
import re
# Create your views here.

CATEGORY_REGEXP = "^\d+_\d+$" # match 30_402 or 402_302 etc.

def dispatcher(request):
  old_id = request.GET.get('products_id', False)
  try:
    old_id = int(old_id)
  except:
    return HttpResponsePermanentRedirect('/')
  category_ids = request.GET.get('cPath', False)
  if category_ids and re.search(CATEGORY_REGEXP, category_ids):
    category_id_list = category_ids.split("_") 
  else:
    category_id_list = None
  if old_id and not category_id_list:
    try:
      product = Product.published.get(old_id=old_id)
      return HttpResponsePermanentRedirect(reverse('product_page', kwargs={ 'slug': product.slug }))
    except:
      return HttpResponsePermanentRedirect('/')
  elif old_id and category_id_list:
    try:
      category = Category.objects.get(old_id=category_id_list[-1])
    except Category.MultipleObjectsReturned:
      category = Category.objects.get(old_id=category_id_list[-1])[0]
    except:
      try:
        category = Category.objects.get(old_id=category_id_list[0])
      except:
        return HttpResponsePermanentRedirect('/')
    try:
      product = Product.published.get(old_id=old_id)
      return HttpResponsePermanentRedirect(reverse('category_product_page', kwargs={ 'slug': product.slug, 'category_slug':category.slug }))
    except:
      return HttpResponsePermanentRedirect('/')
  else:
    return HttpResponsePermanentRedirect('/')
