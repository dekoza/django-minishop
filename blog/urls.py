from blog.models import *
from django.conf.urls.defaults import *

info_dict = {
    'queryset': Post.objects.filter(is_published=True),
    }

post_page = {
    'queryset': Post.objects.filter(is_published=True),
    'slug_field': 'slug'
    }


urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^wpis/(?P<slug>[-\w]+)/$', 'object_detail', dict(post_page), name="post_page"),
    url(r'$', 'object_list', dict(info_dict), name="blog_index"),
    )
