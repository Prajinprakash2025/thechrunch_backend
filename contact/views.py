from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import ContactMessage
from .serializers import ContactMessageSerializer

from accounts.permissions import IsAdminOrStaff, IsSuperAdmin 

# ============================================================
# 📄 PAGINATION CLASS (12 items per page)
# ============================================================
class ContactPagination(PageNumberPagination):
    page_size = 12  
    page_size_query_param = 'page_size'
    max_page_size = 50

# ============================================================
# 1️⃣ PUBLIC CONTACT CREATE VIEW
# ============================================================
class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]  # Public access

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "status": True,
                "message": "Your message has been sent successfully.",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

# ============================================================
# 2️⃣ ADMIN CONTACT LIST VIEW (With Search & Pagination)
# ============================================================
class AdminContactListView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        contacts = ContactMessage.objects.all().order_by("-created_at")
        
        search_query = request.query_params.get('search', '')
        
        if search_query:
            contacts = contacts.filter(
                Q(full_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        paginator = ContactPagination()
        paginated_contacts = paginator.paginate_queryset(contacts, request, view=self)
        
        serializer = ContactMessageSerializer(paginated_contacts, many=True)
        
        return Response({
            "status": True,
            "message": "Contacts retrieved successfully",
            "total_items": paginator.page.paginator.count,
            "total_pages": paginator.page.paginator.num_pages,
            "current_page": paginator.page.number,
            "next_page_url": paginator.get_next_link(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# ============================================================
# 3️⃣ ADMIN CONTACT DETAIL VIEW
# ============================================================
class AdminContactDetailView(generics.RetrieveAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminOrStaff]

# ============================================================
# 4️⃣ ADMIN CONTACT DELETE VIEW
# ============================================================
class AdminContactDeleteView(generics.DestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsSuperAdmin]

# ============================================================
# 5️⃣ ADMIN EMAIL REPLY VIEW
# ============================================================
class AdminContactReplyView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        contact_message = get_object_or_404(ContactMessage, pk=pk)
        reply_text = request.data.get("reply_message")

        if not reply_text:
            return Response(
                {"status": False, "message": "Reply message cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subject = f"Re: {contact_message.subject} - The Crunch"
        message = f"Dear {contact_message.full_name},\n\n{reply_text}\n\nBest Regards,\nThe Crunch Team"
        from_email = settings.EMAIL_HOST_USER  

        try:
            send_mail(
                subject, 
                message, 
                from_email, 
                [contact_message.email], 
                fail_silently=False
            )
            
            return Response({
                "status": True,
                "message": f"Reply sent successfully to {contact_message.email}!"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": False,
                "message": f"Failed to send email. Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)