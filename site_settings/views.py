from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import SiteSetting
from .serializers import SiteSettingSerializer
from accounts.permissions import IsAdminOrStaff # Your custom permission

class SiteSettingRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteSettingSerializer

    def get_permissions(self):
        # Allow anyone to view settings (GET)
        if self.request.method == 'GET':
            return [AllowAny()]
        # Only Admin/Staff can update settings (PUT/PATCH)
        return [IsAdminOrStaff()]

    def get_object(self):
        # Fetch the first object, or create it if it doesn't exist (ID=1)
        obj, created = SiteSetting.objects.get_or_create(pk=1)
        return obj