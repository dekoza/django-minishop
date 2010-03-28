from products.models import Product
from django.shortcuts import render_to_response, get_object_or_404
from stock.forms import StockChangeForm, StockFilterForm
from stock.models import StockLog
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.

@staff_member_required
def product_list(request, page=0):
  app_label = title = _("Stock")
  if request.method == 'GET':
    #form = StockFilterForm()
    form = StockFilterForm(request.GET)
    get_string = ""
    get_list = []
    if form.is_valid():
      query = form.cleaned_data.get('query', None)
      category = form.cleaned_data.get('category', None)
      manufacturer = form.cleaned_data.get('manufacturer', None)
      order = form.cleaned_data.get('order', None)
      order_by = form.cleaned_data.get('order_by', None)
      ordering = order+order_by
      products = Product.objects.all()
      if query and query != '':
        products = products.filter(name__icontains=query)
        get_list.append("query="+query)
      if category:
        products = products.filter(categories=category)
        get_list.append("category="+str(category.pk))
      if manufacturer:
        products = products.filter(manufacturer=manufacturer)
        get_list.append("manufacturer="+str(manufacturer))
      try:
        products = products.order_by(ordering)
        get_list.append("order="+str(order))
        get_list.append("order_by="+str(order_by))
      except:
        pass
      try:
        get_string = "?"+get_list.pop(0)
        if len(get_list) == 1: 
          get_string += "&"+get_list[0]
        elif len(get_list) == 0:
          pass
        else:
          get_string += "&"+ "&".join(get_list)
      except:
        get_string = ""
    else:
      products = Product.objects.all()
    
    # prevents 404
    if int(products.count()/40)+1 < int(page):
      print 'why? leo?'
      page = 0

  return list_detail.object_list(
      request,
      queryset=products,
      paginate_by=40,
      page=page,
      allow_empty=True,
      template_name='admin/stock_product_list.html',
      extra_context={'app_label':app_label, 'title':title, 'form':form, 'get_string':get_string})

@staff_member_required
def product_detail(request, product_id):
  product = get_object_or_404(Product, pk=product_id)
  logs = StockLog.objects.filter(product=product)
  if request.method == 'GET':
    form = StockChangeForm(initial={'quantity':product.quantity})
    return render_to_response('admin/stock_product_detail.html', {
      'form': form,
      'product': product,
      'logs': logs,
      'title':_("Procuct: %s" % product.name),
      'app_label': _("Stock management"),
      }, context_instance=RequestContext(request)) 
  else:
    form = StockChangeForm(request.POST)
    if form.is_valid():
      quantity = form.cleaned_data['quantity']
      description = form.cleaned_data['description']
      user = form.cleaned_data['user']
      product.quantity = quantity
      product._stock_log_meta = {'description':description, 'user':user}
      product.save()
      return render_to_response('admin/stock_product_detail.html', {
        'form': form,
        'product': product,
        'logs': logs,
        'title':_("Procuct: %s" % product.name),
        'app_label': _("Stock management"),
        }, context_instance=RequestContext(request)) 
    else:
      return render_to_response('admin/stock_product_detail.html', {
        'form': form,
        'product': product,
        'logs': logs,
        'title':_("Procuct: %s" % product.name),
        'app_label': _("Stock management"),
        }, context_instance=RequestContext(request)) 
