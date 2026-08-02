from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for booking system
    is_bookable = models.BooleanField(default=False, help_text="Enable booking for this product")
    booking_price_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Price per day for booking"
    )
    min_booking_days = models.PositiveIntegerField(default=1, help_text="Minimum days required for booking")
    max_booking_days = models.PositiveIntegerField(default=30, help_text="Maximum days allowed for booking")
    available_quantity_for_booking = models.PositiveIntegerField(
        default=1, 
        help_text="Number of units available for booking"
    )
    
    # New field for wishlist
    wishlist_count = models.PositiveIntegerField(default=0, db_index=True, help_text="Number of users who added this to wishlist")

    def __str__(self):
        return self.name
    
    def get_availability_for_date_range(self, start_date, end_date):
        """Check if product is available for given date range"""
        from bookings.models import ProductBooking, BookingStatus
        from django.db.models import Sum
        
        # Get total booked quantity for the date range
        booked_quantity = ProductBooking.objects.filter(
            product=self,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            start_date__lt=end_date,
            end_date__gt=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate available quantity
        available = self.available_quantity_for_booking - booked_quantity
        return max(0, available)
    
    def get_total_bookings(self):
        """Get total number of bookings for this product"""
        from bookings.models import ProductBooking, BookingStatus
        return self.bookings.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).count()

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.cartitem_set.all())
    
    def total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())
    
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    shipping_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    def get_total_items(self):
        return sum(item.quantity for item in self.orderitem_set.all())
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"