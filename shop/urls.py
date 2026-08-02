from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    
    # Buy Now URL
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Order URLs
    path('orders/', views.order_history, name='order_history'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # API/AJAX URLs
    path('api/cart-total/', views.get_cart_total, name='get_cart_total'),
    path('api/quick-add-to-cart/', views.quick_add_to_cart, name='quick_add_to_cart'),
    path('add-multiple-to-cart/', views.add_multiple_to_cart, name='add_multiple_to_cart'),
]