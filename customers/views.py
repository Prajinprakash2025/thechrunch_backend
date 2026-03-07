import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from accounts.models import User
from rest_framework.response import Response
from rest_framework import generics, status, filters
from .serializers import CustomerSerializer # Serializer import cheyyan marakkutha

# ==========================================
# 1. LIST & SEARCH CUSTOMERS API
# ==========================================
class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser] # Admin-u mathrame list kaanan pattu
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'phone_number']

    def get_queryset(self):
        # Admin ozhichulla baaki ella regular users-neyum return cheyyunnu
        # accounts/models.py-ile 'role' field 'user' aayavar mathram
        return User.objects.filter(is_superuser=False, role='user').order_by('-date_joined')

# ==========================================
# 2. TOGGLE BLOCK/UNBLOCK CUSTOMER API
# ==========================================
class ToggleBlockCustomerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # accounts/models.py-ile 'is_blocked' field toggle cheyyunnu
            user.is_blocked = not user.is_blocked 
            user.save()
            
            status_text = "blocked" if user.is_blocked else "unblocked"
            return Response({"message": f"User successfully {status_text}."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# 3. EXPORT CUSTOMERS TO CSV (Excel Fixed)
# ==========================================
class ExportCustomersCSV(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # CSV response set cheyyunnu
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crunch_customers.csv"'

        writer = csv.writer(response)
        # Header row - Excel-il ee order-il aanu columns varuka
        writer.writerow(['Customer ID', 'First Name', 'Last Name', 'Phone Number', 'Email', 'Joined Date', 'Account Status'])

        # Role 'user' aaya ellavareyum database-il ninnu edukunnu
        customers = User.objects.filter(role='user')

        for user in customers:
            # is_blocked field check cheythu status string aakkunnu
            acc_status = "Blocked" if getattr(user, 'is_blocked', False) else "Active"
            joined_date = user.date_joined.strftime('%Y-%m-%d') if user.date_joined else ""
            
            # 🚀 THE EXCEL FIX: Prepending a single quote (')
            # Excel-il phone number scientific notation aavathe 'Full' aayi kaanaan
            phone_number_text = f"'{user.phone_number}" if user.phone_number else ""
            
            # Row ezhuthunnu
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