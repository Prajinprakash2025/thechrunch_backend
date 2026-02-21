from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import TableBooking
from .serializers import TableBookingSerializer
from accounts.permissions import IsAdminOrStaff 
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class BookingPagination(PageNumberPagination):
    page_size = 8  # Oru thavana 8 data mathram
    page_size_query_param = 'page_size'
    max_page_size = 50

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
        
        search_query = request.query_params.get('search', '')
        
        if search_query:
            bookings = bookings.filter(
                Q(full_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # 3. Pagination Apply 
        paginator = BookingPagination()
        paginated_bookings = paginator.paginate_queryset(bookings, request, view=self)
        
        serializer = TableBookingSerializer(paginated_bookings, many=True)
        
        # 5. Frontend-nu avashyamulla ella details-um response aayi kodukkuka
        return Response({
            "status": True,
            "message": "Bookings retrieved successfully",
            "total_items": paginator.page.paginator.count,   # Aake ethra bookings und
            "total_pages": paginator.page.paginator.num_pages, # Aake ethra pages und
            "current_page": paginator.page.number,           # Ippol ethamathe page aanu
            "next_page_url": paginator.get_next_link(),      # Adutha 8 data edukkanulla URL
            "data": serializer.data                          # Ee page-le 8 data
        }, status=status.HTTP_200_OK)
    

