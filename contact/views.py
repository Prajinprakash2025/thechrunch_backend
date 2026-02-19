from .serializers import ContactMessageSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .permissions import IsSuperAdmin



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
                "message": "Thank you. Your message has been sent successfully.",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )




class AdminContactListView(generics.ListAPIView):

    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageSerializer
    permission_classes = [IsSuperAdmin]


class AdminContactDetailView(generics.RetrieveAPIView):

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsSuperAdmin]


class AdminContactDeleteView(generics.DestroyAPIView):

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsSuperAdmin]



