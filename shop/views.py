from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return redirect('product_detail', product_id=product_id)

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    
    if cart.cartitem_set.count() == 0:
        return redirect('cart_view') # Don't let them check out with an empty cart
        
    # Create the Order
    order = Order.objects.create(
        user=request.user,
        total_price=cart.total_price()
    )
    
    # Copy items from Cart to Order
    for item in cart.cartitem_set.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    
    # Empty the cart
    cart.delete()
    
    return render(request, 'shop/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    # Get all orders for the current user, newest first
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})