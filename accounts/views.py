from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneOTP
from .serializers import (
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer
)

User = get_user_model()


# ============================================================
# 1️⃣ PASSWORD LOGIN
# Superadmin / Owner / Employee
# ============================================================
class LoginView(APIView):

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
        if user.is_superuser:
            role = "superadmin"

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
# Customer login start
# ============================================================
class SendOTPView(APIView):

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
# Customer login complete
# ============================================================
class VerifyOTPView(APIView):

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
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        if otp_obj.is_expired():
            otp_obj.delete()
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark verified
        otp_obj.is_verified = True
        otp_obj.save()

        # Create customer if not exists
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "role": "customer"
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



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner   # or IsSuperAdmin

User = get_user_model()


class CreateEmployeeView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")

        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            role="employee"
        )

        return Response({
            "status": True,
            "message": "Employee created successfully",
            "username": user.username
        }, status=status.HTTP_201_CREATED)
