from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

# Phone number validation rule
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# -------------------------------
# 1. Password Login Serializer (Admin/Staff)
# -------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )

        if not user:
            raise serializers.ValidationError(
                {"error": "Invalid username or password"}
            )
            
        if not user.is_active:
            raise serializers.ValidationError(
                {"error": "This account has been disabled."}
            )

        data["user"] = user
        return data


# -------------------------------
# 2. Send / Resend OTP Serializer
# -------------------------------
class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[phone_regex], 
        max_length=15
    )


# -------------------------------
# 3. Verify OTP Serializer
# -------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[phone_regex], 
        max_length=15
    )
    
    # Strictly enforce 6 digits to fix your Postman error
    otp = serializers.CharField(max_length=6, min_length=6)
    
    # Added these so the Verify API can create the user!
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value