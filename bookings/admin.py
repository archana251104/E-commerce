from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'user', 'product', 'event_date', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking_number', 'user__username', 'product__name']
    readonly_fields = ['booking_number', 'created_at', 'updated_at']