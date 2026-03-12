from rest_framework import generics
from rest_framework.permissions import AllowAny
from accounts.permissions import IsAdminOrStaff  # <-- Ninte custom permission import cheythu
from .models import FAQ
from .serializers import FAQSerializer

# 🌍 PUBLIC API: Frontend-il kanikkan (Active aayathu mathram)
class PublicFAQListView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True).order_by('created_at')
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

# 🛡️ ADMIN & STAFF APIs: Admin panel-il add/edit/delete cheyyan
class AdminFAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all().order_by('-created_at')
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrStaff]  # <-- Ippo Admin/Staff randalkkum idukkam

class AdminFAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrStaff]  # <-- Ippo Admin/Staff randalkkum edit/delete cheyyam