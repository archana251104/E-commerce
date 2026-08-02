from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from shop.models import Order

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to our store.")
            return redirect('product_list')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('product_list')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('product_list')

@login_required
def profile(request):
    """User profile view showing user details and order history"""
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Calculate total spent
    total_spent = sum(order.total_price for order in orders if order.total_price)
    
    context = {
        'user': user,
        'orders': orders,
        'total_orders': orders.count(),
        'total_spent': total_spent,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def order_history(request):
    """View order history for the logged-in user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/order_history.html', context)

@login_required
def edit_profile(request):
    """Edit user profile information"""
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Check if username is taken by another user
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'accounts/edit_profile.html', {'user': user})
        
        user.username = username
        user.email = email
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if current password is correct
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'accounts/change_password.html')
        
        # Check if new password matches confirmation
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'accounts/change_password.html')
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/change_password.html')
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate user
        login(request, user)
        messages.success(request, "Password changed successfully!")
        return redirect('profile')
    
    return render(request, 'accounts/change_password.html')