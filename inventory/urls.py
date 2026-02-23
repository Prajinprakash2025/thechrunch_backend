from django.urls import path
from . import views

urlpatterns = [
    # --- CATEGORY URLS ---
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # --- SECTION URLS ---
    path('sections/', views.SectionListCreateView.as_view(), name='section-list'),
    path('sections/<int:pk>/', views.SectionDetailView.as_view(), name='section-detail'),

    # --- MENU ITEM URLS ---
    # Public Endpoint (List only, no pagination)
    path('public/menu-items/', views.PublicMenuItemListView.as_view(), name='public-menu-list'),
    
    # Admin Endpoint (List & Create, with pagination)
    path('admin/menu-items/', views.AdminMenuItemListCreateView.as_view(), name='admin-menu-list'),
    
    # Detail Endpoint (GET is public, PUT/PATCH/DELETE is Admin)
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
]