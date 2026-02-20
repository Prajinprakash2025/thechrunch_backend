from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import TableBooking
from .serializers import TableBookingSerializer
from accounts.permissions import IsAdminOrStaff 

# ============================================================
# 1️⃣ CREATE BOOKING
# public access 
# ============================================================
class CreateBookingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TableBookingSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
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
# Can only see admin and staff (Protected)
# ============================================================
class ListBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request):
        bookings = TableBooking.objects.all().order_by('-created_at')
        serializer = TableBookingSerializer(bookings, many=True)
        
        return Response({
            "status": True,
            "message": "Bookings retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)