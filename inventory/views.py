from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q  

from accounts.permissions import IsAdminOrStaff 
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer

# ==========================================
# CUSTOM PAGINATION
# ==========================================
class AdminPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ==========================================
# CATEGORY VIEWS (Unchanged)
# ==========================================
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrStaff()]  

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrStaff()]  

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

class PublicCategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  


# ==========================================
# MENU ITEM VIEWS 
# ==========================================
class PublicMenuItemListView(generics.ListAPIView):
    serializer_class = MenuItemSerializer
    pagination_class = None 

    def get_queryset(self):
        # 🌟 OPTIMIZATION: Added prefetch_related('variants') to speed up the API!
        queryset = MenuItem.objects.prefetch_related('variants').filter(is_available=True).order_by('-created_at')
        
        # 2. Read the Query Parameters 
        search_query = self.request.query_params.get('search', '')
        category_id = self.request.query_params.get('category', '')
        section_name = self.request.query_params.get('section', '')
        diet_pref = self.request.query_params.get('diet', '')  
        
        # 3. Apply the filters safely
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) 
            )
            
        if category_id and str(category_id).upper() != 'ALL':
            queryset = queryset.filter(category_id=category_id)
            
        if section_name and str(section_name).upper() != 'ALL':
            queryset = queryset.filter(section__iexact=section_name)
            
        if diet_pref and str(diet_pref).upper() != 'ALL':
            queryset = queryset.filter(dietary_preference__iexact=diet_pref)

        return queryset
    
    
class AdminMenuItemListCreateView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrStaff]  
    pagination_class = AdminPagination 

    def get_queryset(self):
        # 🌟 OPTIMIZATION: Added prefetch_related('variants')
        queryset = MenuItem.objects.prefetch_related('variants').all().order_by('-created_at')
        
        search_query = self.request.query_params.get('search', '')
        category_id = self.request.query_params.get('category', '')
        section_name = self.request.query_params.get('section', '')
        low_stock = self.request.query_params.get('low_stock', '')
        is_available_param = self.request.query_params.get('available', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) 
            )
            
        if category_id and str(category_id).upper() != 'ALL':
            queryset = queryset.filter(category_id=category_id)
            
        if section_name and str(section_name).upper() != 'ALL':
            queryset = queryset.filter(section__iexact=section_name)
            
        # 🌟 NEW LOGIC: Apply Low Stock Filter for BOTH regular items and variants
        if low_stock and str(low_stock).lower() == 'true':
            queryset = queryset.filter(
                # Condition A: It has NO variants, and the main quantity is < 10
                Q(has_variants=False, quantity__lt=10) | 
                # Condition B: It HAS variants, and any of the variant quantities are < 10
                Q(has_variants=True, variants__quantity__lt=10)
            ).distinct() # Use distinct() so items don't show up twice if multiple sizes are low stock!
            
        if is_available_param:
            if str(is_available_param).lower() == 'true':
                queryset = queryset.filter(is_available=True)
            elif str(is_available_param).lower() == 'false':
                queryset = queryset.filter(is_available=False)
            
        return queryset

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    # 🌟 OPTIMIZATION: Added prefetch_related('variants')
    queryset = MenuItem.objects.prefetch_related('variants').all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminOrStaff()]  

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