import csv
from django.http import HttpResponse
from rest_framework import generics, views, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import CustomerSerializer

User = get_user_model()

# ==========================================
# 1. LIST & SEARCH CUSTOMERS API
# ==========================================
class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser] # Only admins can view this
    filter_backends = [filters.SearchFilter]
    # Admin can search by first_name, last_name, or phone_number
    search_fields = ['first_name', 'last_name', 'phone_number']

    def get_queryset(self):
        # Return only regular users (exclude admins/staff if needed)
        return User.objects.filter(is_superuser=False).order_by('-date_joined')

# ==========================================
# 2. TOGGLE BLOCK/UNBLOCK API
# ==========================================
class ToggleBlockCustomerView(views.APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        # Prevent admin from blocking themselves
        if user == request.user or user.is_superuser:
            return Response({"error": "Cannot block an admin user."}, status=status.HTTP_400_BAD_REQUEST)

        # Toggle the status
        user.is_blocked = not user.is_blocked
        user.save()

        status_text = "blocked" if user.is_blocked else "unblocked"
        return Response({"message": f"User successfully {status_text}."}, status=status.HTTP_200_OK)

# ==========================================
# 3. EXPORT CUSTOMERS TO CSV (Google Sheets compatible)
# ==========================================
class ExportCustomersCSV(APIView):
    permission_classes = [IsAuthenticated] # Add admin permissions if needed

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crunch_customers.csv"'

        writer = csv.writer(response)
        # Write the header row
        writer.writerow(['Customer ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Joined Date', 'Account Status'])

        # Fetch all users with role 'user'
        customers = User.objects.filter(role='user')

        for user in customers:
            status = "Blocked" if getattr(user, 'is_blocked', False) else "Active"
            joined_date = user.date_joined.strftime('%Y-%m-%d') if user.date_joined else ""
            
            # 🚀 THE FIX: Wrapping the phone number in an Excel text formula
            phone_number_text = f'="{user.phone_number}"' if user.phone_number else ""
            
            # Write data rows
            writer.writerow([
                user.id,
                user.first_name,
                user.last_name,
                phone_number_text,
                user.email,
                joined_date,
                status
            ])

        return response