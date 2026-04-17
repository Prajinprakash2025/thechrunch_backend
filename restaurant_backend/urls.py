from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Contact App
    path('api/', include('contact.urls')),
    
    # 🌟 ALL Auth, Login, Registration & Profile routes are now handled here
    path("api/auth/", include("accounts.urls")),
    
    # Other Apps
    path('api/bookings/', include('bookings.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/banners/', include('banners.urls')),
    path('api/site-settings/', include('site_settings.urls')),
    path('api/orders/', include('orders.urls')),
    
    # Customer & Management Apps
    path('api/customers/', include('customers.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/revenue/', include('revenue.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/faq/', include('faq.urls')),
]

# Static & Media files configuration for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)