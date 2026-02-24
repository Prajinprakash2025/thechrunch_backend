from .serializers import ContactMessageSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from accounts.permissions import IsAdminOrStaff 
from accounts.permissions import IsSuperAdmin 




class ContactCreateView(generics.CreateAPIView):

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]  # Public access

    def create(self, request, *args, **kwargs):

        # Let DRF handle validation + save
        response = super().create(request, *args, **kwargs)

        # Wrap response in standardized format
        return Response(
            {
                "status": True,
                "message": "Your message has been sent successfully.",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )




class AdminContactListView(generics.ListAPIView):

    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminOrStaff]


class AdminContactDetailView(generics.RetrieveAPIView):

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminOrStaff]


class AdminContactDeleteView(generics.DestroyAPIView):

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsSuperAdmin]



# ============================================================
# 📧 ADMIN EMAIL REPLY VIEW
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