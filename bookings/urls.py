from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('create/<int:product_id>/', views.create_booking, name='create_booking'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('check-availability/', views.check_availability, name='check_availability'),
]