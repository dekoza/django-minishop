from products.models import Manufacturer

def manufacturers(request):
  manufacturers = Manufacturer.objects.all()
  return {'manufacturers': manufacturers}
