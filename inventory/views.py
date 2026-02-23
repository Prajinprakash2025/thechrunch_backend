from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

# IMPORTANT: Import the updated permission from your accounts app!
from accounts.permissions import IsAdminUser 

from .models import Category, Section, MenuItem
from .serializers import CategorySerializer, SectionSerializer, MenuItemSerializer

# ==========================================
# CUSTOM PAGINATION
# ==========================================
class AdminPagination(PageNumberPagination):
    page_size = 10 # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==========================================
# CATEGORY VIEWS
# ==========================================
class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories (Public)
    POST: Create a new category (Admin only)
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
    PUT/PATCH: Update a category (Admin only)
    DELETE: Delete a category (Admin only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": True,
            "message": "Category updated successfully!",
            "data": response.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": True,
            "message": "Category deleted successfully!"
        }, status=status.HTTP_200_OK)


# ==========================================
# SECTION VIEWS
# ==========================================
class SectionListCreateView(generics.ListCreateAPIView):
    """
    GET: List all sections (Public)
    POST: Create a new section (Admin only)
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific section (Public)
    PUT/PATCH: Update a section (Admin only)
    DELETE: Delete a section (Admin only)
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": True,
            "message": "Section updated successfully!",
            "data": response.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": True,
            "message": "Section deleted successfully!"
        }, status=status.HTTP_200_OK)


# ==========================================
# MENU ITEM VIEWS (Split for User vs Admin)
# ==========================================

# 1️⃣ PUBLIC VIEW (Customer App)
class PublicMenuItemListView(generics.ListAPIView):
    """
    GET: List all available menu items for the customer app (No Pagination)
    """
    # Only returns items where is_available=True
    queryset = MenuItem.objects.filter(is_available=True).order_by('-created_at') 
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny] 
    pagination_class = None # Explicitly disabled for public

# 2️⃣ ADMIN VIEW (Dashboard)
class AdminMenuItemListCreateView(generics.ListCreateAPIView):
    """
    GET: List ALL menu items with pagination (Admin only)
    POST: Create a new menu item (Admin only)
    """
    queryset = MenuItem.objects.all().order_by('-created_at')
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser] 
    pagination_class = AdminPagination 

# 3️⃣ DETAIL VIEW (Used by both)
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific menu item (Public)
    PUT/PATCH: Update a menu item (Admin only)
    DELETE: Delete a menu item (Admin only)
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        # Public can view a single item, Admin can edit/delete
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": True,
            "message": "Menu Item updated successfully!",
            "data": response.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": True,
            "message": "Menu Item deleted successfully!"
        }, status=status.HTTP_200_OK)