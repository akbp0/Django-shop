from .cart import Cart


def cart_processor(request):
    return {'carts': Cart(request)}

