from orders.cart import Cart

def shopping_cart(request):
  c = Cart(request)
  return {'cart': c,
      'cdebug':request.session.get('cart_new',0) 
      }
