from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import OrderForm
import uuid

def home(request):
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True, 
        stock__gt=0
    )[:8]
    
    new_products = Product.objects.filter(
        is_active=True, 
        stock__gt=0
    ).order_by('-created_at')[:8]
    
    categories = Category.objects.all()
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
        'cart_count': cart_count,
    }
    return render(request, 'shop/home.html', context)

def get_cart_count(request):
    """Helper function to get cart count"""
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.get_total_items()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()
            if cart:
                cart_count = cart.get_total_items()
    return cart_count

def product_list(request):
    products = Product.objects.filter(is_active=True, stock__gt=0)
    categories = Category.objects.all()
    
    # Category filter
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            products = products.filter(category=current_category)
        else:
            messages.warning(request, 'Category not found.')
    
    # Search filter
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply sorting based on the parameter
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == '-created_at':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'cart_count': cart_count,
    }
    return render(request, 'shop/product_list.html', context)
    
  

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_count': cart_count,
    }
    return render(request, 'shop/product_detail.html', context)

def get_or_create_cart(request):
    """Get or create a cart for the user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('shop:product_detail', slug=product.slug)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available.')
        return redirect('shop:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity + quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} items available.')
            return redirect('shop:product_detail', slug=product.slug)
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    
    cart_item.save()
    messages.success(request, f'{product.name} added to cart!')
    
    next_url = request.POST.get('next', 'shop:cart')
    return redirect(next_url)

def view_cart(request):
    """View the cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total(),
        'cart_count': cart_count,
    }
    return render(request, 'shop/cart.html', context)

def update_cart(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, 'Not enough stock available.')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.info(request, 'Item removed from cart.')
        elif action == 'remove':
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
        
        return redirect('shop:cart')
    
    return redirect('shop:cart')

@login_required
def checkout(request):
    """Checkout process"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f'ORD-{uuid.uuid4().hex[:10].upper()}'
            order.total_amount = cart.get_total()
            order.save()
            
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            cart.items.all().delete()
            
            messages.success(request, f'Order placed successfully! Order #{order.order_number}')
            return redirect('shop:order_confirmation', order_id=order.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
            # If you have a profile model
            if hasattr(request.user, 'profile'):
                initial_data['phone'] = request.user.profile.phone if hasattr(request.user.profile, 'phone') else ''
                initial_data['address'] = request.user.profile.address if hasattr(request.user.profile, 'address') else ''
        form = OrderForm(initial=initial_data)
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total(),
        'form': form,
        'cart_count': cart_count,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    return render(request, 'shop/order_confirmation.html', {
        'order': order,
        'cart_count': cart_count,
    })

@login_required
def order_history(request):
    """Order history page"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Get cart count for navbar
    cart_count = get_cart_count(request)
    
    return render(request, 'shop/order_history.html', {
        'orders': orders,
        'cart_count': cart_count,
    })

def buy_now(request, product_id):
    """Buy now functionality - adds product to cart and redirects to checkout"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('shop:product_detail', slug=product.slug)
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available.')
        return redirect('shop:product_detail', slug=product.slug)
    
    # Clear existing cart and add this product
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    
    CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    
    if request.user.is_authenticated:
        return redirect('shop:checkout')
    else:
        messages.info(request, 'Please login to checkout.')
        return redirect('accounts:login')