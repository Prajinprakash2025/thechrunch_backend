from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics
from .utils import send_whatsapp_otp  # 🌟 ഇംപോർട്ട് ചേർക്കുക
from .models import PhoneOTP, Address
from .serializers import LoginSerializer, VerifyOTPSerializer, UserProfileSerializer, AddressSerializer
from .permissions import IsAdminUser

User = get_user_model()

# ============================================================
# CUSTOM JWT LOGIN TO HANDLE BLOCKED USERS
# ============================================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_blocked:
            raise AuthenticationFailed("Your account has been blocked. Please contact Crunch.")
        return data

class CustomTokenLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ============================================================
# 1. ADMIN & STAFF: PASSWORD LOGIN
# ============================================================
class LoginView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        # Check if user is blocked
        if user.is_blocked:
            return Response({"status": False, "message": "Your account has been blocked. Please contact Crunch."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        if user.is_superuser and not user.role:
            role = "admin" 
        elif user.role:
            role = user.role
        else:
            role = "unknown"

        return Response({
            "status": True,
            "message": "Login successful",
            "role": role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# ============================================================
# 2. OTP FLOW: SIGNUP - STEP 1 (Request OTP)
# ============================================================
class SignupRequestOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp_requests' 

    def post(self, request):
        phone = request.data.get("phone_number")
        name = request.data.get("name", "")
        email = request.data.get("email", "")

        if not phone or not name:
            return Response({"status": False, "message": "Phone and Name are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone).exists():
            return Response({"status": False, "message": "User already exists. Please login."}, status=status.HTTP_400_BAD_REQUEST)

        otp_instance, created = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.name = name   
        otp_instance.email = email 
        otp_instance.generate_otp() 
        
        # 🌟 WhatsApp വഴി OTP അയക്കുന്നു
        send_whatsapp_otp(phone, otp_instance.otp)
        
        return Response({
            "status": True, 
            "message": "OTP sent via WhatsApp!",
            "data": {"test_otp": otp_instance.otp} # ടെസ്റ്റിംഗ് കഴിഞ്ഞ് ഇത് മാറ്റാം
        }, status=status.HTTP_200_OK)


# ============================================================
# 3. OTP FLOW: SIGNUP & LOGIN - STEP 2 (Resend OTP)
# ============================================================
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp_requests' 

    def post(self, request):
        phone = request.data.get("phone_number")

        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone)
            
            if otp_instance.is_data_expired():
                otp_instance.delete()
                return Response({"status": False, "message": "Session expired. Please start signup again."}, status=status.HTTP_400_BAD_REQUEST)

            otp_instance.generate_otp()

            # 🌟 WhatsApp വഴി പുതിയ OTP അയക്കുന്നു
            send_whatsapp_otp(phone, otp_instance.otp)

            return Response({
                "status": True, 
                "message": "New OTP sent via WhatsApp!",
                "data": {"test_otp": otp_instance.otp}
            }, status=status.HTTP_200_OK)

        except PhoneOTP.DoesNotExist:
            return Response({"status": False, "message": "No session found. Please request OTP first."}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# 4. OTP FLOW: SIGNUP & LOGIN - STEP 3 (Verify OTP)
# ============================================================
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone, otp=otp)
        except PhoneOTP.DoesNotExist:
            return Response({"status": False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_instance.is_otp_expired():
            return Response({"status": False, "message": "OTP expired. Please click resend."}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "first_name": otp_instance.name if otp_instance.name else "",
                "email": otp_instance.email if otp_instance.email else "",
                "role": "user"
            }
        )
        
        if user.is_blocked:
            return Response({"status": False, "message": "Your account has been blocked. Please contact Crunch."}, status=status.HTTP_403_FORBIDDEN)

        if created:
            user.set_unusable_password()
            user.save()

        otp_instance.delete()

        refresh = RefreshToken.for_user(user)
        
        # --- Ivideyanu change varuthiyath ---
        return Response({
            "status": True,
            "message": "Verification successful!",
            "first_name": user.first_name, # <-- Puthiyathayi add cheythathu
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# ============================================================
# 5. OTP FLOW: LOGIN - STEP 1 (Request Login OTP)
# ============================================================
class LoginRequestOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp_requests' 

    def post(self, request):
        phone = request.data.get("phone_number")

        try:
            user = User.objects.get(phone_number=phone)
            if user.is_blocked:
                return Response({"status": False, "message": "Your account has been blocked. Please contact Crunch."}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Please Signup"}, status=status.HTTP_400_BAD_REQUEST)

        otp_instance, created = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()

        # 🌟 WhatsApp വഴി OTP അയക്കുന്നു
        send_whatsapp_otp(phone, otp_instance.otp)

        return Response({
            "status": True, 
            "message": "Login OTP sent via WhatsApp!",
            "data": {"test_otp": otp_instance.otp}
        }, status=status.HTTP_200_OK)


# ============================================================
# 6. ADMIN UTILITY: CREATE STAFF 
# ============================================================
class CreateStaffView(APIView): 
    permission_classes = [IsAuthenticated, IsAdminUser] 

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")

        if not username or not password:
            return Response({"status": False, "message": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"status": False, "message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            role="staff" 
        )

        return Response({
            "status": True,
            "message": "Staff account created successfully",
            "username": user.username
        }, status=status.HTTP_201_CREATED)


# ============================================================
# 7. SESSION UTILITIES (Verify Token & Logout)
# ============================================================
class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "authenticated": True,
            "user_id": request.user.id,
            "username": request.user.username
        })
    

# ============================================================
# 8. USER PROFILE (View & Update)
# ============================================================
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated] 

    def get_object(self):
        return self.request.user


# ============================================================
# 9. ADDRESS MANAGEMENT
# ============================================================
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-id')

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)