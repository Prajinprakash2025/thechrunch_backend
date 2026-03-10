from django.urls import path
from .views import AdminDashboardView

urlpatterns = [
    path('admin-stats/', AdminDashboardView.as_view(), name='admin_dashboard_stats'),
]