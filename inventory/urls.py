from django.urls import path
from .views import (
    CategoryListCreateView, 
    CategoryDetailView,
    MenuItemListCreateView,
    MenuItemDetailView
)

urlpatterns = [
    # ==========================================
    # CATEGORY ENDPOINTS
    # ==========================================
    # GET: List all / POST: Add new
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    
    # GET: View one / PUT: Edit / DELETE: Remove
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # ==========================================
    # MENU ITEM ENDPOINTS
    # ==========================================
    # GET: List all / POST: Add new
    path('menu-items/', MenuItemListCreateView.as_view(), name='menu-item-list'),
    
    # GET: View one / PUT: Edit / DELETE: Remove
    path('menu-items/<int:pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
]   