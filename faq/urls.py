from django.urls import path
from .views import (
    PublicFAQListView, 
    AdminFAQListCreateView, 
    AdminFAQUpdateView, 
    AdminFAQDeleteView
)

urlpatterns = [
    # 🌍 Public URL
    path('list/', PublicFAQListView.as_view(), name='public-faq-list'),

    # 🛡️ Admin URLs
    path('admin/list-create/', AdminFAQListCreateView.as_view(), name='admin-faq-list-create'),
    path('admin/edit/<int:pk>/', AdminFAQUpdateView.as_view(), name='admin-faq-edit'),
    path('admin/delete/<int:pk>/', AdminFAQDeleteView.as_view(), name='admin-faq-delete'),
]