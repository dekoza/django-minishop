from django.conf.urls.defaults import *

urlpatterns = patterns('seoredirect.views',
    url(r'^$', 'dispatcher', name="seo_dispatcher"),
    )
