from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ContactMessage

class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    permission_classes = [permissions.AllowAny] # Public access

    def create(self, request, *args, **kwargs):
        # 1. Validate the data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. Save to database
        self.perform_create(serializer)
        
        # 3. Return a nice success message
        return Response(
            {
                "status": "success",
                "message": "Thank you! Your message has been sent successfullyyy.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )