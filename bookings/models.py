from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from shop.models import Product

User = get_user_model()

class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CANCELLED = 'cancelled', 'Cancelled'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'

class ProductBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    booking_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Status and pricing
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    
    # Additional information
    special_requests = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Booking"
        verbose_name_plural = "Product Bookings"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.product.name} by {self.user.username}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date")
        if self.start_date < timezone.now():
            raise ValidationError("Start date cannot be in the past")
        
        # Check for overlapping bookings
        if self.pk:
            overlapping = ProductBooking.objects.filter(
                product=self.product,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
            ).exclude(pk=self.pk).filter(
                start_date__lt=self.end_date,
                end_date__gt=self.start_date
            )
            if overlapping.exists():
                raise ValidationError("This product is already booked for the selected dates")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_total_price(self):
        days = (self.end_date - self.start_date).days
        return self.product.booking_price_per_day * days * self.quantity

class BookingPayment(models.Model):
    booking = models.OneToOneField(ProductBooking, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_successful = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for Booking #{self.booking.id}"