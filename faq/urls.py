from django.urls import path
from .views import PublicFAQListView, AdminFAQListCreateView, AdminFAQDetailView

urlpatterns = [
    # Public URL (For Website)
    path('list/', PublicFAQListView.as_view(), name='public-faq-list'),

    # Admin URLs (For Admin Dashboard)
    path('admin/list-create/', AdminFAQListCreateView.as_view(), name='admin-faq-list-create'),
    path('admin/<int:pk>/', AdminFAQDetailView.as_view(), name='admin-faq-detail'),
]