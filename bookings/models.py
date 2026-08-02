from django.db import models
from django.contrib.auth.models import User
from shop.models import Product

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    booking_number = models.CharField(max_length=20, unique=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    duration = models.CharField(max_length=50, help_text="e.g., 2 hours, Full day")
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Booking {self.booking_number} - {self.user.username}'