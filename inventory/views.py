from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer

# IMPORTANT: Import the updated permission from your accounts app!
from accounts.permissions import IsAdminUser 

# ==========================================
# CATEGORY VIEWS
# ==========================================

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories (Public)
    POST: Create a new category (Admin/Superadmin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific category (Public)
    PUT/PATCH: Update a category (Admin/Superadmin only)
    DELETE: Delete a category (Admin/Superadmin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]


# ==========================================
# MENU ITEM VIEWS
# ==========================================

class MenuItemListCreateView(generics.ListCreateAPIView):
    """
    GET: List all menu items (Public)
    POST: Create a new menu item (Admin/Superadmin only)
    """
    queryset = MenuItem.objects.all().order_by('-created_at')
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()] 

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific menu item (Public)
    PUT/PATCH: Update a menu item (Admin/Superadmin only)
    DELETE: Delete a menu item (Admin/Superadmin only)
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]