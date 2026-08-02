from accounts import views  # <--- Add this line at the top
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    
    # This uses Django's built-in authentication
    path('accounts/', include('django.contrib.auth.urls')), 
    path('accounts/register/', views.register, name='register'), # We will handle registration separately
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)