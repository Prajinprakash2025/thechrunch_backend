from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
from rest_framework import serializers


class UnifiedLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    otp = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def validate(self, data):

        # Case 1: Username + password login
        if data.get("username") and data.get("password"):
            return data

        # Case 2: Phone OTP send
        if data.get("phone_number") and not data.get("otp"):
            return data

        # Case 3: Phone OTP verify
        if data.get("phone_number") and data.get("otp"):
            return data

        raise serializers.ValidationError("Invalid login request")
