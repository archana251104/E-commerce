from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),  # <--- This connects to shop/urls.py
    path('accounts/', include('accounts.urls')),
]