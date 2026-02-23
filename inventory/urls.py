from django.urls import path
from . import views

urlpatterns = [
    # --- CATEGORY URLS ---
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # --- MENU ITEM URLS ---
    path('public/menu-items/', views.PublicMenuItemListView.as_view(), name='public-menu-list'),
    path('admin/menu-items/', views.AdminMenuItemListCreateView.as_view(), name='admin-menu-list'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
]