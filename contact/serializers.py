from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny] # Keeps it public

    # I added this custom method to send a nice message back
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # This returns a custom JSON response
        return Response(
            {
                "status": "success",
                "message": "Thank you! Your message has been sent successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )