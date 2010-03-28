from orders.models import Order, OrderedItem


class Filter():
  def __init__(self, queryset, request):
    self.queryset = queryset
    self.request = request
