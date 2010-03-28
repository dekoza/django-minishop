from django.conf.urls.defaults import *

urlpatterns = patterns('xmloutput.views',
    url(r'^kangoo.xml$', 'xml_kangoo', name="xml_kangoo"),
    url(r'^okazje.xml$', 'xml_okazje', name="xml_okazje"),
                      )

