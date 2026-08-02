from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Product
from .models import Booking
import uuid

@login_required
def create_booking(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        duration = request.POST.get('duration')
        special_requests = request.POST.get('special_requests', '')
        
        booking = Booking.objects.create(
            user=request.user,
            product=product,
            booking_number=f'BOK-{uuid.uuid4().hex[:10].upper()}',
            event_date=event_date,
            event_time=event_time,
            duration=duration,
            special_requests=special_requests
        )
        
        messages.success(request, f'Booking created successfully! Booking #{booking.booking_number}')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    return render(request, 'bookings/create_booking.html', {'product': product})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel this booking.')
    return redirect('bookings:my_bookings')