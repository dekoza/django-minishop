from django import template
from django.db.models import Q
from products.models import Product, Category, CategoryRecommendation

register = template.Library()

def related_products(product):
  #related = Product.published.exclude(pk=product.pk).filter(Q(manufacturer=product.manufacturer) | Q(categories__in=product.categories.all()) | Q(solutions__in=product.solutions.all())).distinct()[:3]
  related = Product.published.exclude(pk=product.pk).filter(Q(solutions__in=product.solutions.all()) | Q(manufacturer=product.manufacturer)).distinct()[:3]
  return {'related_products':related}

def nett(value):
  try:
    from settings import TAX_RATE
  except:
    TAX_RATE = 0.22
  from decimal import Decimal
  if isinstance(value, (Decimal, float, int)):
    v = float(value)
    return v-(v*TAX_RATE)
  else:
    return value

def tax_rate(value):
  try:
    from settings import TAX_RATE
  except:
    TAX_RATE = 0.22
  from decimal import Decimal
  if isinstance(value, (Decimal, float, int)):
    v = float(value)
    return v*TAX_RATE
  else:
    return value

class GetProductBadge(template.Node):
    def __init__(self, category, product):
        self.category = template.Variable(category)
        self.product = template.Variable(product)
    def render(self,context):
        print self.category, self.product
        recommendation = CategoryRecommendation.objects.get(category=self.category.resolve(context), product=self.product.resolve(context))
        if recommendation.type == 0:
            return ''
        elif recommendation.type == 1:
            return '<div class="badge_new"></div>'
        elif recommendation.type == 2:
            return '<div class="badge_recommended"></div>'
        else:
            return ''

def get_product_badge(parser, token):
    try:
        tag_name, category, product = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents.split()[0]
    return GetProductBadge(category, product)

register.inclusion_tag('products/related.html')(related_products)
register.tag('get_product_badge', get_product_badge)
register.filter('nett', nett)
register.filter('tax_rate', tax_rate)
