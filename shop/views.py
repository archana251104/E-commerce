from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import OrderForm
import uuid

def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True, stock__gt=0)[:8]
    new_products = Product.objects.filter(is_active=True, stock__gt=0).order_by('-created_at')[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True, stock__gt=0)
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)

def get_or_create_cart(request):
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
    product = get_object_or_404(Product, id=product_id)
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
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total(),
    }
    return render(request, 'shop/cart.html', context)

def update_cart(request, item_id):
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
        elif action == 'remove':
            cart_item.delete()
        
        return redirect('shop:cart')
    
    return redirect('shop:cart')

@login_required
def checkout(request):
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
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.profile.phone,
            'address': request.user.profile.address,
        }
        form = OrderForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total(),
        'form': form,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})

def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'Sorry, only {product.stock} items available.')
        return redirect('shop:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    
    CartItem.objects.create(cart=cart, product=product, quantity=quantity)
    
    if request.user.is_authenticated:
        return redirect('shop:checkout')
    else:
        messages.info(request, 'Please login to checkout.')
        return redirect('accounts:login')