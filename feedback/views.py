from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order  
from accounts.permissions import IsAdminOrStaff


# 1. Frontend-nu review tab kanikkano ennu check cheyyanulla API
class ReviewEligibilityCheckView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # User-nte peril oru DELIVERED order engilum undengil True return cheyyum
        has_delivered_order = Order.objects.filter(
            user=request.user, 
            order_status='DELIVERED'
        ).exists()
        
        return Response({"is_eligible": has_delivered_order})

# 2. Review Submit cheyyanulla API
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Backend Security: Delivered order illengil block cheyyum!
        has_delivered_order = Order.objects.filter(
            user=request.user, 
            order_status='DELIVERED'
        ).exists()

        if not has_delivered_order:
            return Response(
                {"error": "You can only leave a review after receiving at least one delivered order."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validation pass aayal review save cheyyum
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user) # Login cheytha aalude id automatic aayi edukkum
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 3. Homepage-il reviews kanikkanulla API (Public)
class ReviewListView(generics.ListAPIView):
    # Approved aaya reviews mathram latest aadyam varunna pole kanikkum
    queryset = Review.objects.filter(is_approved=True).order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]