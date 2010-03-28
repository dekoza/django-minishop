from products.models import Product
from products.models import Category as PCategory
from blog.models import *
from voting.models import *
from slideshow.models import Slide

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.utils import translation
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import list_detail
from django.contrib.comments.models import Comment

def index(request):
    latest = Product.published.all().order_by('-created')[:6]
    bestsellers_votes = list(Vote.objects.get_top(Product, limit=3))
    bestsellers = [b[0] for b in bestsellers_votes]
    blog = Post.objects.filter(is_published=True, frontpage=True)
    if len(blog):
        blog = blog[0]
    try:
        frontpage_category = PCategory.objects.get(pk=1)
        recommendations = frontpage_category.recommended
    except PCategory.DoesNotExist:
        frontpage_category = None
        recommendations = None

    slideshow = Slide.objects.all()
    comments = Comment.objects.filter(is_public=True, is_removed=False).order_by('-submit_date')
    if len(comments) > 0:
        comments = comments[:3]
    return render_to_response('front.html',
            {
                    'recommendations':recommendations,
                    'latest_products':latest,
                    'bestsellers':bestsellers,
                    'blog':[blog],
                    'category':frontpage_category,
                    'slideshow':slideshow,
                    'comments':comments
            },
            context_instance=RequestContext(request))
