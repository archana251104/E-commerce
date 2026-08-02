from .models import Cart

def cart_count(request):
    """Context processor to add cart count to all templates"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart_count': cart.total_items()}
    return {'cart_count': 0}