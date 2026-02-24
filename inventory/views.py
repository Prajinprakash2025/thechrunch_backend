from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q  # <-- Added for native search filtering

from accounts.permissions import IsAdminUser 
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer

# ==========================================
# CUSTOM PAGINATION
# ==========================================
class AdminPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

# ==========================================
# CATEGORY VIEWS
# ==========================================
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
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
# MENU ITEM VIEWS 
# ==========================================

from rest_framework import generics
from django.db.models import Q
from .models import MenuItem
from .serializers import MenuItemSerializer

class PublicMenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    pagination_class = None 

    def get_queryset(self):
        # 1. Start with all available items
        queryset = MenuItem.objects.filter(is_available=True).order_by('-created_at')
        
        # 2. Read the Query Parameters (?search=...&category=...)
        search_query = self.request.query_params.get('search', '')
        category_id = self.request.query_params.get('category', '')
        section_name = self.request.query_params.get('section', '')
        
        # 3. Apply the filters safely
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        if category_id and str(category_id).upper() != 'ALL':
            queryset = queryset.filter(category_id=category_id)
            
        if section_name and str(section_name).upper() != 'ALL':
            queryset = queryset.filter(section__iexact=section_name)
            
        return queryset

class AdminMenuItemListCreateView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser] 
    pagination_class = AdminPagination 

    def get_queryset(self):
        # 1. Start with ALL items (including unavailable ones for the admin)
        queryset = MenuItem.objects.all().order_by('-created_at')
        
        # 2. Get the parameters from the frontend URL
        search_query = self.request.query_params.get('search', '')
        category_id = self.request.query_params.get('category', '')
        section_name = self.request.query_params.get('section', '')
        
        # 3. Apply Text Search
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        # 4. Apply Category Filter
        if category_id and str(category_id).upper() != 'ALL':
            queryset = queryset.filter(category_id=category_id)
            
        # 5. Apply Section Filter
        if section_name and str(section_name).upper() != 'ALL':
            queryset = queryset.filter(section__iexact=section_name)
            
        return queryset

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
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