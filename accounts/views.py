from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneOTP
from .serializers import (
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer
)
from .permissions import IsAdminUser   # <-- Updated from IsOwner

User = get_user_model()


# ============================================================
# 1️⃣ PASSWORD LOGIN
# Superadmin / Admin / Staff
# ============================================================
class LoginView(APIView):
    permission_classes = [AllowAny] # Ensures anyone can access the login page

    def post(self, request):
        # Validate request data
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # --------------------------------------------------
        # Resolve Role Properly
        # --------------------------------------------------
        if user.is_superuser and not user.role:
            role = "admin" # Default superusers to admin for the frontend
        elif user.role:
            role = user.role
        else:
            role = "unknown"

        # --------------------------------------------------
        # Response
        # --------------------------------------------------
        return Response({
            "status": True,
            "message": "Login successful",
            "role": role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# ============================================================
# 2️⃣ SEND OTP
# User login start
# ============================================================
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]

        # Delete old OTP records
        PhoneOTP.objects.filter(phone_number=phone).delete()

        # Create new OTP
        otp_obj = PhoneOTP.objects.create(phone_number=phone)
        otp_obj.generate_otp()
        otp_obj.save()

        print(f"OTP for {phone}: {otp_obj.otp}")

        return Response({
            "status": True,
            "message": "OTP sent successfully",
            # ⚠️ REMOVE THIS IN PRODUCTION
            "otp": otp_obj.otp
        }, status=status.HTTP_200_OK)


# ============================================================
# 3️⃣ VERIFY OTP
# User login complete
# ============================================================
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        # Check OTP record
        try:
            otp_obj = PhoneOTP.objects.get(
                phone_number=phone,
                otp=otp
            )
        except PhoneOTP.DoesNotExist:
            return Response(
                {"status": False, "message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        if otp_obj.is_expired():
            otp_obj.delete()
            return Response(
                {"status": False, "message": "OTP expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark verified
        otp_obj.is_verified = True
        otp_obj.save()

        # Create user if not exists
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "role": "user"   # <-- CHANGED FROM "customer" TO "user"
            }
        )

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        # Delete OTP after use
        otp_obj.delete()

        return Response({
            "status": True,
            "message": "Login successful",
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# ============================================================
# 4️⃣ CREATE STAFF 
# Admin Only
# ============================================================
class CreateStaffView(APIView): # <-- Renamed to match your new roles

    # <-- CHANGED permission from IsOwner to IsAdminUser
    permission_classes = [IsAuthenticated, IsAdminUser] 

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")

        if not username or not password:
            return Response(
                {"status": False, "message": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"status": False, "message": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            role="staff"    # <-- CHANGED FROM "employee" TO "staff"
        )

        return Response({
            "status": True,
            "message": "Staff account created successfully",
            "username": user.username
        }, status=status.HTTP_201_CREATED)



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "authenticated": True,
            "user_id": request.user.id,
            "username": request.user.username
        })


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() # ടോക്കൺ ബ്ലാക്ക്‌ലിസ്റ്റ് ചെയ്യുന്നു
            return Response({"message": "Successfully logged out"}, status=205)
        except Exception as e:
            return Response(status=400)