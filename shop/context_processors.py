from .models import Cart
from wishlist.models import Wishlist

def cart_count(request):
    """
    Context processor to get the total number of items in the cart.
    Works for both authenticated and anonymous users.
    """
    count = 0
    
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
    """
    Context processor to get the total number of items in the wishlist.
    Only works for authenticated users.
    """
    count = 0
    
    if request.user.is_authenticated:
        try:
            count = Wishlist.objects.filter(user=request.user).count()
        except:
            count = 0
    else:
        count = 0
    
    return {'wishlist_count': count}

def cart_total(request):
    """
    Context processor to get the total amount of the cart.
    """
    total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total = cart.get_total()
        except Cart.DoesNotExist:
            total = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key, user=None)
                total = cart.get_total()
            except Cart.DoesNotExist:
                total = 0
        else:
            total = 0
    
    return {'cart_total': total}