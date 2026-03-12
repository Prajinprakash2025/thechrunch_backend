from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

# Import the new custom view to handle blocked users on default JWT route
from accounts.views import CustomTokenLoginView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('contact.urls')),
    path("api/auth/", include("accounts.urls")),

    # Updated to use CustomTokenLoginView for blocking functionality
    path('api/token/', CustomTokenLoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/bookings/', include('bookings.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/banners/', include('banners.urls')),
    path('api/site-settings/', include('site_settings.urls')),
    path('api/orders/', include('orders.urls')),  
    
    # 🌟 NEW APP FOR MANAGING CUSTOMERS
    path('api/customers/', include('customers.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/revenue/', include('revenue.urls')),
    path('api/feedback/', include('feedback.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)