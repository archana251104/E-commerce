from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.my_bookings, name='my_bookings'),
    path('create/<int:product_id>/', views.create_booking, name='create_booking'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]