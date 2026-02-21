from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from rest_framework.response import Response
from rest_framework import status

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

    # 1️⃣ EDIT (PUT/PATCH) 
    def update(self, request, *args, **kwargs):
        # Default update calling function
        response = super().update(request, *args, **kwargs)
        
        return Response({
            "status": True,
            "message": "Category updated successfully!",
            "data": response.data
        }, status=status.HTTP_200_OK)

    # 2️⃣ DELETE 
    def destroy(self, request, *args, **kwargs):
        # any category finding
        instance = self.get_object()
        
        # deleting the category
        self.perform_destroy(instance)
        
        return Response({
            "status": True,
            "message": "Category deleted successfully!"
        }, status=status.HTTP_200_OK)


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