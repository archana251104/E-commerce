from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import ProductBooking, BookingStatus
from shop.models import Product
from .forms import BookingForm

@login_required
def booking_list(request):
    bookings = ProductBooking.objects.filter(user=request.user)
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bookings': page_obj,
    }
    return render(request, 'bookings/booking_list.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(ProductBooking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def create_booking(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_bookable=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, product=product)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.product = product
            booking.total_price = booking.calculate_total_price()
            booking.save()
            
            messages.success(request, f'Booking created successfully for {product.name}')
            return redirect('bookings:booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(product=product)
    
    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'bookings/create_booking.html', context)

@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(ProductBooking, id=booking_id, user=request.user)
    
    if booking.status == BookingStatus.PENDING:
        booking.status = BookingStatus.CANCELLED
        booking.save()
        messages.success(request, 'Booking cancelled successfully')
    else:
        messages.error(request, 'Cannot cancel this booking')
    
    return redirect('bookings:booking_detail', booking_id=booking.id)

@login_required
@require_POST
def check_availability(request):
    product_id = request.POST.get('product_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    
    if not all([product_id, start_date, end_date]):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    product = get_object_or_404(Product, id=product_id)
    from datetime import datetime
    from django.utils import timezone
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    if start < timezone.now():
        return JsonResponse({'error': 'Start date cannot be in the past'}, status=400)
    
    available_quantity = product.get_availability_for_date_range(start, end)
    days = (end - start).days
    
    return JsonResponse({
        'available': available_quantity > 0,
        'available_quantity': available_quantity,
        'total_price': float(product.booking_price_per_day or 0) * days,
        'daily_price': float(product.booking_price_per_day or 0),
        'days': days
    })