from django.urls import path
from .views import RevenueDashboardView

urlpatterns = [
    path('profit-tracker/', RevenueDashboardView.as_view(), name='profit_tracker'),
]