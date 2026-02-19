from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import TableBooking
from .serializers import TableBookingSerializer 

class BookingCreateView(generics.ListCreateAPIView):
    queryset = TableBooking.objects.all()
    serializer_class = TableBookingSerializer 

    def get_permissions(self):
        if self.request.method == 'POST':
            # Allow anyone to book a table
            return [permissions.AllowAny()]
        elif self.request.method == 'GET':
            # Only allow admin and superadmin to view the bookings
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                "status": "success",
                "message": "Your table has been booked successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )