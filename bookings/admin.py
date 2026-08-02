from django.contrib import admin
from .models import ProductBooking, BookingPayment

class BookingPaymentInline(admin.StackedInline):
    model = BookingPayment
    extra = 1

@admin.register(ProductBooking)
class ProductBookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'start_date', 'end_date', 'status', 'total_price']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BookingPaymentInline]
    
    actions = ['confirm_bookings', 'cancel_bookings']
    
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} bookings confirmed")
    
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} bookings cancelled")