from rest_framework import generics
from rest_framework.permissions import AllowAny
from accounts.permissions import IsAdminOrStaff
from .models import FAQ
from .serializers import FAQSerializer

# 🌍 PUBLIC API: Website-il kanikkan (Backend-il thanne 5 aayi limit cheythirikkunnu)
class PublicFAQListView(generics.ListAPIView):
    # Ippo queryset-nte avasanam [:5] koduthittundu. Athayathu 5 ennam mathram.
    queryset = FAQ.objects.all().order_by('created_at')[:5] 
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

# 🛡️ ADMIN API: List cheyyanum puthiyathu add cheyyanum
class AdminFAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all().order_by('-created_at')
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrStaff]

# ✏️ ADMIN API: Edit cheyyan mathram (Update Only)
class AdminFAQUpdateView(generics.RetrieveUpdateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrStaff]

# 🗑️ ADMIN API: Delete cheyyan mathram
class AdminFAQDeleteView(generics.DestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrStaff]