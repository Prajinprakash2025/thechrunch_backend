from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from .permissions import IsOwner # Importing your updated custom permission

# ==========================================
# CATEGORY VIEWS
# ==========================================

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories (Public)
    POST: Create a new category (Owner/Superadmin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOwner()]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific category (Public)
    PUT/PATCH: Update a category (Owner/Superadmin only)
    DELETE: Delete a category (Owner/Superadmin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOwner()]


# ==========================================
# MENU ITEM VIEWS
# ==========================================

class MenuItemListCreateView(generics.ListCreateAPIView):
    """
    GET: List all menu items (Public)
    POST: Create a new menu item (Owner/Superadmin only)
    """
    queryset = MenuItem.objects.all().order_by('-created_at')
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOwner()] 

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific menu item (Public)
    PUT/PATCH: Update a menu item (Owner/Superadmin only)
    DELETE: Delete a menu item (Owner/Superadmin only)
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsOwner()]