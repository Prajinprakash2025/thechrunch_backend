from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import PhoneOTP
from .serializers import LoginSerializer, VerifyOTPSerializer
from .permissions import IsAdminUser

User = get_user_model()


# ============================================================
# 1️⃣ ADMIN & STAFF: PASSWORD LOGIN
# ============================================================
class LoginView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
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
# 2️⃣ OTP FLOW: SIGNUP - STEP 1 (Request OTP)
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

        # 1. Check Permanent Table
        if User.objects.filter(phone_number=phone).exists():
            return Response({"status": False, "message": "User already exists. Please login."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Update or Create Temp Store & Generate OTP
        otp_instance, created = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.name = name   
        otp_instance.email = email 
        otp_instance.generate_otp() 
        
        return Response({
            "status": True, 
            "message": "OTP sent! Data saved to temp store.",
            "data": {"test_otp": otp_instance.otp}
        }, status=status.HTTP_200_OK)


# ============================================================
# 3️⃣ OTP FLOW: SIGNUP & LOGIN - STEP 2 (Resend OTP)
# ============================================================
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp_requests' 

    def post(self, request):
        phone = request.data.get("phone_number")

        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone)
            
            # Clean-up: If temp data is older than 24h, delete it.
            if otp_instance.is_data_expired():
                otp_instance.delete()
                return Response({"status": False, "message": "Session expired. Please start signup again."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate new OTP (resets 2-min timer)
            otp_instance.generate_otp()
            return Response({
                "status": True, 
                "message": "New OTP sent!",
                "data": {"test_otp": otp_instance.otp}
            }, status=status.HTTP_200_OK)

        except PhoneOTP.DoesNotExist:
            return Response({"status": False, "message": "No session found. Please request OTP first."}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# 4️⃣ OTP FLOW: SIGNUP & LOGIN - STEP 3 (Verify OTP)
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

        # Check 2-minute timer
        if otp_instance.is_otp_expired():
            return Response({"status": False, "message": "OTP expired. Please click resend."}, status=status.HTTP_400_BAD_REQUEST)

        # Move from Temp Store to Permanent Table
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "first_name": otp_instance.name if otp_instance.name else "",
                "email": otp_instance.email if otp_instance.email else "",
                "role": "user"
            }
        )
        
        if created:
            user.set_unusable_password()
            user.save()

        # Clean-up Temp Data
        otp_instance.delete()

        # Generate JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            "status": True,
            "message": "Verification successful!",
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# ============================================================
# 5️⃣ OTP FLOW: LOGIN - STEP 1 (Request Login OTP)
# ============================================================
class LoginRequestOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'otp_requests' 

    def post(self, request):
        phone = request.data.get("phone_number")

        # 1. Check Permanent Table
        if not User.objects.filter(phone_number=phone).exists():
            return Response({"status": False, "message": "Please Signup"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Save to Temp Store & Generate OTP (No name/email needed)
        otp_instance, created = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()

        return Response({
            "status": True, 
            "message": "Login OTP sent!",
            "data": {"test_otp": otp_instance.otp}
        }, status=status.HTTP_200_OK)


# ============================================================
# 6️⃣ ADMIN UTILITY: CREATE STAFF 
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
# 7️⃣ SESSION UTILITIES (Verify Token & Logout)
# ============================================================
class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "authenticated": True,
            "user_id": request.user.id,
            "username": request.user.username
        })


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