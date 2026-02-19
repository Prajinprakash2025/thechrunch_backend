from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PhoneOTP
from .serializers import UnifiedLoginSerializer

User = get_user_model()


class UnifiedLoginView(APIView):

    def post(self, request):

        serializer = UnifiedLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # =========================
        # 1️⃣ Username + Password
        # =========================
        if data.get("username") and data.get("password"):

            user = authenticate(
                username=data["username"],
                password=data["password"]
            )

            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)

            return Response({
                "role": user.role,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })


        # =========================
        # 2️⃣ Send OTP
        # =========================
        if data.get("phone_number") and not data.get("otp"):

            phone = data["phone_number"]

            otp_obj, _ = PhoneOTP.objects.get_or_create(
                phone_number=phone
            )

            otp_obj.generate_otp()
            otp_obj.is_verified = False
            otp_obj.save()

            return Response({
                "message": "OTP sent",
                "otp": otp_obj.otp  # REMOVE IN PRODUCTION
            })


        # =========================
        # 3️⃣ Verify OTP
        # =========================
        if data.get("phone_number") and data.get("otp"):

            phone = data["phone_number"]
            otp = data["otp"]

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

            if otp_obj.is_expired():
                return Response(
                    {"error": "OTP expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user, _ = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    "username": phone,
                    "role": "customer"
                }
            )

            refresh = RefreshToken.for_user(user)

            otp_obj.delete()

            return Response({
                "role": user.role,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
