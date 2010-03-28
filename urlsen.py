from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from biolander.admin import admin_site
admin.autodiscover()
from products.models import Product
from voting.views import xmlhttprequest_vote_on_object, vote_on_object
from chartstats.chart import DateChartView

urlpatterns = patterns('',
    # Example:
    # (r'^biolander/', include('biolander.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'views.index'),
    (r'^imaging/', include('biolander.imaging.urls')),
    (r'^users/', include('biolander.customers.urls')),
    (r'^products/', include('biolander.products.urls')),
    (r'^index.php$', include('biolander.seoredirect.urls')),
    # dotpay - must appear BEFORE orders urls. odd
    url(r'^thankyou/$', 'django.views.generic.simple.direct_to_template', {'template': 'orders/thankyou.html'}, name="landing_page"),
    url(r'^wxd2rob/$', 'orders.admin_views.dotpay_reponse', name="dotpay_response"),
    (r'^orders/', include('biolander.orders.urls')),
    (r'^newsletter/', include('biolander.newsletter.urls')),
    (r'^tinymce/', include('tinymce.urls')),
#    (r'^search/', 'products.views.search'),
    (r'^blog/', include('biolander.blog.urls')),
    (r'^newsletter/register/', 'products.views.newsletter'),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^vote/(?P<slug>[-\w]+)/(?P<direction>[1-5]+)/$', xmlhttprequest_vote_on_object, { 'model': Product, 'slug_field': 'slug' }, name='product-vote'),

    # admin views
    url(r'^admin/orders/all/$', 'orders.admin_views.show_orders', name="admin_orders_all", kwargs={'type':0}),
    url(r'^admin/orders/all/page/(?P<page>[0-9]+)/$', 'orders.admin_views.show_orders', name="admin_orders_all_paginated", kwargs={'type':0}),
    url(r'^admin/orders/new/$', 'orders.admin_views.show_orders', name="admin_orders_needing_action", kwargs={'type':1}),
    url(r'^admin/orders/low_stock/$', 'orders.admin_views.show_orders', name="admin_orders_low_stock", kwargs={'type':2}),
    url(r'^admin/orders/paid/$', 'orders.admin_views.show_orders', name="admin_orders_paid", kwargs={'type':3}),
    url(r'^admin/order/status/(?P<order_id>\d+)/$', 'orders.admin_views.change_status', name="order_change_status"),
    url(r'^admin/order/review/(?P<order_id>\d+)/$', 'orders.admin_views.review_order', name="review_order"),
    url(r'^admin/stock/review/(?P<product_id>\d+)/$', 'stock.views.product_detail', name="stock_product_detail"),
    url(r'^admin/stock/$', 'stock.views.product_list', name="stock_product_list"),
    url(r'^admin/stock/page/(?P<page>[0-9]+)/$', 'stock.views.product_list', name="stock_product_list_paginated"),
    (r'^admin/products/category/$', 'products.views.tree_list', {'model': 'categories'}),
    (r'^admin/products/solution/$', 'products.views.tree_list', {'model': 'solutions'}),
    # old fashion SiteAdmin admin
    (r'^classic_admin/(.*)', admin.site.root),
    # overriden SiteAdmin admin
    (r'^admin/(.*)', admin_site.root),
    (r'^grappelli/', include('grappelli.urls')),
    # chart test
    (r'^charcik/$', DateChartView() ),
    #(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/pielgrzym/www/biolander/media/'}),

)
