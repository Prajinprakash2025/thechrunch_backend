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
class ExportCustomersCSVView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crunch_customers.csv"'

        writer = csv.writer(response)
        # CSV Header Row
        writer.writerow(['Customer ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Joined Date', 'Account Status'])

        users = User.objects.filter(is_superuser=False).order_by('-date_joined')
        for user in users:
            status_text = "Blocked" if user.is_blocked else "Active"
            # Write data rows
            writer.writerow([
                user.id, 
                user.first_name, 
                user.last_name, 
                user.phone_number, 
                user.email, 
                user.date_joined.strftime("%Y-%m-%d"), 
                status_text
            ])

        return response