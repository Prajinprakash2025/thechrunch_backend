from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import TableBooking
from .serializers import TableBookingSerializer
from accounts.permissions import IsAdminOrStaff ,IsNotBlocked
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from notifications.models import AdminNotification  # Added Notification Model Import

class BookingPagination(PageNumberPagination):
    page_size = 12  
    page_size_query_param = 'page_size'
    max_page_size = 50

# ============================================================
# 1️⃣ CREATE BOOKING
# Public access 
# ============================================================
class CreateBookingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TableBookingSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            # --- NOTIFICATION SAVING ---
            # Save notification to database when a new booking is created
            AdminNotification.objects.create(
                notification_type='booking',
                message="New Table Booking received"
            )

            return Response({
                "status": True,
                "message": "Your table has been booked successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "status": False,
            "message": "Booking failed. Please check the details.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# 2️⃣ LIST BOOKINGS
# Protected: Can only be seen by admin and staff
# ============================================================
class ListBookingsView(APIView):
    permission_classes = [IsNotBlocked, IsAdminOrStaff]

    def get(self, request):
        bookings = TableBooking.objects.all().order_by('-created_at')
        
        search_query = request.query_params.get('search', '')
        
        if search_query:
            bookings = bookings.filter(
                Q(full_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # 3. Apply Pagination 
        paginator = BookingPagination()
        paginated_bookings = paginator.paginate_queryset(bookings, request, view=self)
        
        serializer = TableBookingSerializer(paginated_bookings, many=True)
        
        # 5. Provide all necessary details in the response for the frontend
        return Response({
            "status": True,
            "message": "Bookings retrieved successfully",
            "total_items": paginator.page.paginator.count,     # Total number of bookings
            "total_pages": paginator.page.paginator.num_pages, # Total number of pages
            "current_page": paginator.page.number,             # Current page number
            "next_page_url": paginator.get_next_link(),        # URL for the next page of data
            "data": serializer.data                            # Data for the current page
        }, status=status.HTTP_200_OK)