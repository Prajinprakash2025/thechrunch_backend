import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics, status, filters
from rest_framework.pagination import PageNumberPagination
from accounts.models import User
from .serializers import CustomerSerializer

# ==========================================
# CUSTOM PAGINATION CLASS
# ==========================================
class CustomerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ==========================================
# 1. LIST & SEARCH CUSTOMERS API
# ==========================================
class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'phone_number']
    
    # Applying the custom pagination class
    pagination_class = CustomerPagination

    def get_queryset(self):
        # Return only regular users (exclude admins) ordered by newest first
        return User.objects.filter(is_superuser=False, role='user').order_by('-date_joined')

# ==========================================
# 2. TOGGLE BLOCK/UNBLOCK CUSTOMER API
# ==========================================
class ToggleBlockCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_blocked = not user.is_blocked
            user.save()
            
            status_text = "blocked" if user.is_blocked else "unblocked"
            return Response({"message": f"User successfully {status_text}."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# 3. EXPORT CUSTOMERS TO CSV
# ==========================================
class ExportCustomersCSV(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crunch_customers.csv"'

        writer = csv.writer(response)
        
        # Write the header row
        writer.writerow(['Customer ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Joined Date', 'Account Status'])

        # Fetch all users with the role 'user'
        customers = User.objects.filter(role='user')

        for user in customers:
            acc_status = "Blocked" if getattr(user, 'is_blocked', False) else "Active"
            joined_date = user.date_joined.strftime('%Y-%m-%d') if user.date_joined else ""
            
            # Prepend a single quote to prevent Excel from using scientific notation for phone numbers
            phone_number_text = f"'{user.phone_number}" if user.phone_number else ""
            
            # Write user data row
            writer.writerow([
                user.id,
                user.first_name,
                user.last_name,
                phone_number_text,
                user.email,
                joined_date,
                acc_status
            ])

        return response