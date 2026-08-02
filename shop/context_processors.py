from .models import Cart
from wishlist.models import Wishlist

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.get_total_items()
        except Cart.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key, user=None)
                count = cart.get_total_items()
            except Cart.DoesNotExist:
                count = 0
        else:
            count = 0
    return {'cart_count': count}

def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'wishlist_count': count}