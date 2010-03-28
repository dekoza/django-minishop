from django.conf.urls.defaults import *

urlpatterns = patterns('resellers.views',
    url(r'^zarejestruj-sie/$', 'register', name="reseller_register"),
    url(r'^panel/$', 'panel', name="reseller_panel"),
    )

