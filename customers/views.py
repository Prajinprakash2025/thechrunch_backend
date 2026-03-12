import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status, filters
from rest_framework.pagination import PageNumberPagination
from accounts.models import User
from accounts.permissions import IsAdminOrStaff  # Custom permission use cheyyunnu
from .serializers import CustomerSerializer

# ==========================================
# CUSTOM PAGINATION CLASS
# ==========================================
class CustomerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ==========================================
# 1. LIST & SEARCH CUSTOMERS API (With Status Filter)
# ==========================================
class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'phone_number']
    pagination_class = CustomerPagination

    def get_queryset(self):
        # Aadyam ella regular users-neyum edukkunnu
        queryset = User.objects.filter(is_superuser=False, role='user').order_by('-date_joined')
        
        # URL-il ninnu 'status' parameter edukkunnu (?status=blocked or ?status=active)
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter == 'active':
            queryset = queryset.filter(is_blocked=False)
        elif status_filter == 'blocked':
            queryset = queryset.filter(is_blocked=True)
            
        return queryset

# ==========================================
# 2. TOGGLE BLOCK/UNBLOCK CUSTOMER API
# ==========================================
class ToggleBlockCustomerView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, user_id):
        try:
            # ID vechu user-e pidikkunnu
            user = User.objects.get(id=user_id)
            # Status maattunnu (True aayath False aakum, False aayath True aakum)
            user.is_blocked = not user.is_blocked
            user.save()
            
            status_text = "blocked" if user.is_blocked else "unblocked"
            return Response({
                "status": "success",
                "is_blocked": user.is_blocked,
                "message": f"User successfully {status_text}."
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# 3. EXPORT CUSTOMERS TO CSV
# ==========================================
class ExportCustomersCSV(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crunch_customers.csv"'

        writer = csv.writer(response)
        writer.writerow(['Customer ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Joined Date', 'Account Status'])

        customers = User.objects.filter(role='user')

        for user in customers:
            acc_status = "Blocked" if user.is_blocked else "Active"
            joined_date = user.date_joined.strftime('%Y-%m-%d') if user.date_joined else ""
            phone_number_text = f"'{user.phone_number}" if user.phone_number else ""
            
            writer.writerow([
                user.id, user.first_name, user.last_name, 
                phone_number_text, user.email, joined_date, acc_status
            ])

        return response