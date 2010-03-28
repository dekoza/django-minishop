from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from biolander.admin import admin_site
admin.autodiscover()
from products.models import Product
from voting.views import xmlhttprequest_vote_on_object, vote_on_object
from chartstats.chart import DateChartView, SalesByDate
from django.conf import settings

STATIC_MEDIA = getattr(settings, 'STATIC_MEDIA', False)

if STATIC_MEDIA:
    SSL = False
else:
    SSL = True

urlpatterns = patterns('',
    # Example:
    # (r'^biolander/', include('biolander.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'views.index'),
    (r'^imaging/', include('biolander.imaging.urls')),
    (r'^uzytkownicy/', include('biolander.customers.urls'), {'SSL':SSL}),
    (r'^partnerzy/', include('biolander.resellers.urls')),
    (r'^produkty/', include('biolander.products.urls')),
    (r'^index.php$', include('biolander.seoredirect.urls')),
    # dotpay - must appear BEFORE orders urls. odd
    url(r'^dziekujemy/$', 'django.views.generic.simple.direct_to_template', {'template': 'orders/thankyou.html'}, name="landing_page"),
    url(r'^wxd2rob/$', 'orders.admin_views.dotpay_reponse', name="dotpay_response"),
    (r'^zamowienia/', include('biolander.orders.urls'), {'SSL':SSL}),
    (r'^newsletter/', include('biolander.newsletter.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^blog/', include('biolander.blog.urls')),
    (r'^xml/', include('biolander.xmloutput.urls')),
    (r'^komentarze/', include('django.contrib.comments.urls')),
    url(r'^vote/(?P<slug>[-\w]+)/(?P<direction>[1-5]+)/$', xmlhttprequest_vote_on_object, { 'model': Product, 'slug_field': 'slug' }, name='product-vote'),

    # admin views
    url(r'^panel/orders/(?P<type>all|new|low_stock|paid|in_progress)/$', 'orders.admin_views.show_orders', name="admin_orders_list"),
    url(r'^panel/orders/(?P<type>all|new|low_stock|paid|in_progress)/page/(?P<page>[0-9]+)/$', 'orders.admin_views.show_orders', name="admin_orders_list_paginated"),
    url(r'^panel/order/status/(?P<order_id>\d+)/$', 'orders.admin_views.change_status', name="order_change_status"),
    url(r'^panel/order/review/(?P<order_id>\d+)/$', 'orders.admin_views.review_order', name="review_order"),
    url(r'^panel/order/invoice/(?P<type>original|copy)/(?P<order_id>\d+)/$', 'orders.admin_views.order_invoice', name="order_invoice"),
    url(r'^panel/stock/review/(?P<product_id>\d+)/$', 'stock.views.product_detail', name="stock_product_detail"),
    url(r'^panel/stock/$', 'stock.views.product_list', name="stock_product_list"),
    url(r'^panel/stock/page/(?P<page>[0-9]+)/$', 'stock.views.product_list', name="stock_product_list_paginated"),

    url(r'^panel/recommendations/category/$', 'products.admin_views.category_recommendations', name="products_category_recommendations"),
    url(r'^panel/recommendations/(?P<taxonomy_type>category|solution)/save/$', 'products.admin_views.save_recommendations', name="save_recommendations"),
    url(r'^panel/ajax/recommendations/(?P<taxonomy_type>category|solution)/$', 'products.admin_views.ajax_get_recommendations', name="products_ajax_get_recomendations"),
    url(r'^panel/ajax/products/(?P<taxonomy_type>category|solution)/$', 'products.admin_views.ajax_get_products', name="products_ajax_get_products"),

    (r'^panel/products/category/$', 'products.views.tree_list', {'model': 'categories'}),
    (r'^panel/products/solution/$', 'products.views.tree_list', {'model': 'solutions'}),
    # reseller edit override
    url(r'^panel/resellers/partner/(?P<object_id>\d+)/$', 'resellers.admin_views.display_partner', name="resellers_partner_change"),
    url(r'^panel/resellers/partner/activate/(?P<partner_id>\d+)/$', 'resellers.admin_views.toggle_activation', name="resellers_partner_toggle_active"),
    # old fashion SiteAdmin admin
    (r'^classic_admin/(.*)', admin.site.root),
    # overriden SiteAdmin admin
    (r'^panel/(.*)', admin_site.root),
    (r'^grappelli/', include('grappelli.urls')),
    # chart test
    url(r'^stat/total-orders/$', DateChartView(), name="stats_total_orders" ),
    url(r'^stat/total-sales/$', SalesByDate(), name="stats_total_sales"  ),
)

if STATIC_MEDIA:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                           )
