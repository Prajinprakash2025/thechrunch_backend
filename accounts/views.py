from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneOTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer

User = get_user_model()



class SendOTPView(APIView):

    def post(self, request):

        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]

        otp_obj, _ = PhoneOTP.objects.get_or_create(
            phone_number=phone
        )

        otp_obj.generate_otp()
        otp_obj.is_verified = False
        otp_obj.save()

        print(f"OTP for {phone}: {otp_obj.otp}")

        return Response(
            {"message": "OTP sent successfully"},
            status=status.HTTP_200_OK
        )



class VerifyOTPView(APIView):

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

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

        otp_obj.is_verified = True
        otp_obj.save()

        user, _ = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "role": "customer"
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
