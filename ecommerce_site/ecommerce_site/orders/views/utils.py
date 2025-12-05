from orders.models import Cart

def get_user_cart(user):
    return Cart.objects.get_or_create(user=user)[0]
