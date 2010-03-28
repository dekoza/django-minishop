from django.conf.urls.defaults import *
from products.models import *

info_dict = {
    'queryset': Product.published.all(),
    'paginate_by': 5
    }

product_page = {
    'queryset': Product.published.all(),
    'slug_field': 'slug'
    }

certificate_page = {
    'queryset': Certificate.objects.all(),
    'slug_field': 'slug'
    }

urlpatterns = patterns('products.views',
    url(r'^kategoria/(?P<slug>[-\w]+)/$', 'show_category', name="category_page"),
    url(r'^kategoria/(?P<slug>[-\w]+)/str/(?P<page>[0-9]+)/$', 'show_category', name="category_page_paginated"),
    url(r'^kategoria/produkt/(?P<category_slug>[-\w]+)/(?P<slug>[-\w]+)/$', 'show_category_product', name="category_product_page"),
    url(r'^rozwiazanie/(?P<slug>[-\w]+)/$', 'show_solution', name="solution_page"),
    url(r'^rozwiazanie/(?P<slug>[-\w]+)/str/(?P<page>[0-9]+)/$', 'show_solution', name="solution_page_paginated"),
    url(r'^rozwiazanie/produkt/(?P<solution_slug>[-\w]+)/(?P<slug>[-\w]+)/$', 'show_solution_product', name="solution_product_page"),
    url(r'^producent/$', 'manufacturer_list', name="manufacturer_list"),
    url(r'^producent/(?P<slug>[-\w]+)/$', 'show_manufacturer', name="manufacturer_page"),
    url(r'^producent/(?P<slug>[-\w]+)/str/(?P<page>[0-9]+)/$', 'show_manufacturer', name="manufacturer_page_paginated"),
    url(r'^producent/produkt/(?P<manufacturer_slug>[-\w]+)/(?P<slug>[-\w]+)/$', 'show_manufacturer_product', name="manufacturer_product_page"),
    url(r'^szukaj$', 'search', name="search_page"),
    url(r'^szukaj/str/(?P<page>[0-9]+)/$', 'search', name="search_page_paginated_2"),
    url(r'^szukaj/str/(?P<page>[0-9]+)\?q=(?P<q>[\ \-\w]+)$', 'search', name="search_page_paginated"),
)

urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^pokaz/(?P<slug>[-\w]+)/$', 'object_detail', dict(product_page), name="product_page"),
    url(r'^certyfikat/(?P<slug>[-\w]+)/$', 'object_detail', dict(certificate_page), name="certificate_page"),
)

