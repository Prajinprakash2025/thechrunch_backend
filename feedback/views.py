from warnings import filters
from rest_framework import generics, filters
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order  
from accounts.permissions import IsAdminOrStaff
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics

class AdminReviewPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size' 
    max_page_size = 50


class ReviewEligibilityCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Condition 1: User already feedback ittitundengil
        existing_review = Review.objects.filter(user=user).first()
        if existing_review:
            serializer = ReviewSerializer(existing_review)
            return Response({
                "is_eligible": False,
                "has_reviewed": True,
                "message": "You have already submitted your feedback.",
                "review_data": serializer.data  # Frontend-nu kanikkan pazhaya review data
            })

        # Condition 2: Check if user has at least one DELIVERED order
        has_delivered_order = Order.objects.filter(user=user, order_status='DELIVERED').exists()

        if has_delivered_order:
            # Order delivered aayi, pakshe review ittitilla (Show Form)
            return Response({
                "is_eligible": True,
                "has_reviewed": False
            })

        # Condition 3: Order onnum delivered aayitilla (Hide Form)
        return Response({
            "is_eligible": False,
            "has_reviewed": False,
            "message": "Review option will unlock after your first order is delivered! 🍔"
        })

# 2. Review Submit API (Updated to block multiple submissions)
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user

        # SECURITY CHECK 1: User aadyame review ittitundengil block cheyyum!
        if Review.objects.filter(user=user).exists():
            return Response(
                {"error": "You have already submitted your feedback. Multiple submissions are not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # SECURITY CHECK 2: Delivered order illengil block cheyyum!
        has_delivered_order = Order.objects.filter(user=user, order_status='DELIVERED').exists()
        if not has_delivered_order:
            return Response(
                {"error": "You can only leave feedback after receiving at least one delivered order."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Randum pass aayal mathram save cheyyum
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 3. Homepage-il reviews kanikkanulla API (Public)
class ReviewListView(generics.ListAPIView):
    # Approved aaya reviews mathram latest aadyam varunna pole kanikkum
    queryset = Review.objects.filter(is_approved=True).order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]


class AdminReviewListView(generics.ListAPIView):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = AdminReviewPagination 
    
    filter_backends = [filters.SearchFilter]
    
    search_fields = ['user__first_name', 'user__username']

# Admin: Review Approve/Hide cheyyanulla API
class AdminReviewUpdateView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrStaff]