from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Wishlist, WishlistItem
from shop.models import Product

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist.items.select_related('product').all()
    }
    return render(request, 'wishlist/wishlist.html', context)

@login_required
@require_POST
def toggle_wishlist(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    item = WishlistItem.objects.filter(wishlist=wishlist, product=product)
    
    if item.exists():
        item.delete()
        product.wishlist_count -= 1
        product.save()
        action = 'removed'
        message = f"{product.name} removed from wishlist"
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        product.wishlist_count += 1
        product.save()
        action = 'added'
        message = f"{product.name} added to wishlist"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': action,
            'message': message,
            'wishlist_count': product.wishlist_count
        })
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))