from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Cart, CartItem, Order, OrderItem, Category
from wishlist.models import Wishlist, WishlistItem

def product_list(request):
    """Display all products with category filter"""
    category_id = request.GET.get('category')
    products = Product.objects.all()
    categories = Category.objects.all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    """Display product details with related products"""
    product = get_object_or_404(Product, id=product_id)
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=product).exists()
    
    context = {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('shop:product_detail', product_id=product_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Check if adding more exceeds stock
        if cart_item.quantity + 1 > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units of {product.name} available.')
            return redirect('shop:cart_view')
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Updated quantity of {product.name} in your cart.')
    else:
        messages.success(request, f'{product.name} added to your cart!')
    
    return redirect('shop:cart_view')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from your cart.')
    return redirect('shop:cart_view')

@login_required
@require_POST
def update_cart_quantity(request, item_id):
    """Update the quantity of an item in the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    product = cart_item.product
    
    # Check if requested quantity exceeds stock
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} units of {product.name} available.')
        return redirect('shop:cart_view')
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('shop:cart_view')

@login_required
def cart_view(request):
    """View the shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all().select_related('product')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': cart.total_items(),
        'total_price': cart.total_price(),
    }
    return render(request, 'shop/cart.html', context)

@login_required
def clear_cart(request):
    """Clear all items from the cart"""
    cart = get_object_or_404(Cart, user=request.user)
    count = cart.cartitem_set.count()
    cart.cartitem_set.all().delete()
    messages.success(request, f'{count} items removed from your cart.')
    return redirect('shop:cart_view')

@login_required
def checkout(request):
    """Process the checkout"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('shop:cart_view')
    
    if request.method == 'POST':
        with transaction.atomic():
            # Validate stock before creating order
            for cart_item in cart_items:
                if cart_item.quantity > cart_item.product.stock:
                    messages.error(request, f'Sorry, {cart_item.product.name} has insufficient stock.')
                    return redirect('shop:cart_view')
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price(),
                status='pending',
                shipping_address=request.POST.get('shipping_address', ''),
                payment_method=request.POST.get('payment_method', 'cash'),
            )
            
            # Create order items and update stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('shop:order_confirmation', order_id=order.id)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """Show order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    """Show order history for the user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Show detailed view of a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)

@login_required
def get_cart_total(request):
    """AJAX endpoint to get cart total"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return JsonResponse({
        'success': True,
        'total_items': cart.total_items(),
        'total_price': str(cart.total_price()),
        'cart_id': cart.id
    })

@login_required
@require_POST
def quick_add_to_cart(request):
    """AJAX endpoint to quickly add to cart"""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.stock <= 0:
        return JsonResponse({
            'success': False,
            'message': f'Sorry, {product.name} is out of stock.'
        })
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity + 1 > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Sorry, only {product.stock} units of {product.name} available.'
            })
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_total': cart.total_items(),
        'cart_price': str(cart.total_price()),
        'item_quantity': cart_item.quantity
    })

@login_required
@require_POST
def add_multiple_to_cart(request):
    """Add multiple quantities of a product to cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        # Check stock
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units of {product.name} available.')
            return redirect('shop:product_detail', product_id=product_id)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            if cart_item.quantity + quantity > product.stock:
                messages.error(request, f'Sorry, only {product.stock} units of {product.name} available.')
                return redirect('shop:product_detail', product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Added {quantity} x {product.name} to your cart.')
        else:
            messages.success(request, f'{product.name} added to your cart!')
        
        return redirect('shop:cart_view')
    
    return redirect('shop:product_list')

# ========== HELPER FUNCTIONS ==========
def get_cart_count(request):
    """Get cart count for navbar (can be used as context processor)"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return {'cart_count': cart.total_items()}
    return {'cart_count': 0}