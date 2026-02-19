from rest_framework import serializers
from django.contrib.auth import authenticate


# -------------------------------
# Password Login Serializer
# -------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError(
                {"error": "Invalid username or password"}
            )

        data["user"] = user
        return data


# -------------------------------
# Send OTP Serializer
# -------------------------------
class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


# -------------------------------
# Verify OTP Serializer
# -------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
