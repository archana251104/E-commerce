from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_inr', 'compare_price_inr', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def price_inr(self, obj):
        return f"₹{obj.price:,.2f}"
    price_inr.short_description = 'Price (INR)'
    
    def compare_price_inr(self, obj):
        if obj.compare_price:
            return f"₹{obj.compare_price:,.2f}"
        return '-'
    compare_price_inr.short_description = 'Compare Price (INR)'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'get_total_items']
    list_filter = ['created_at']
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_inr', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    def total_inr(self, obj):
        return f"₹{obj.total_amount:,.2f}"
    total_inr.short_description = 'Total (INR)'