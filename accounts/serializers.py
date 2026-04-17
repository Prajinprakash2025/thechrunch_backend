from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import RegexValidator
from .models import Address

User = get_user_model()

# Phone number validation rule
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get("username"),
            password=data.get("password")
        )

        if not user:
            raise serializers.ValidationError({"error": "Invalid username or password"})
            
        if not user.is_active:
            raise serializers.ValidationError({"error": "This account has been disabled."})

        data["user"] = user
        return data

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[phone_regex], max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[phone_regex], max_length=15)
    otp = serializers.CharField(max_length=6, min_length=6)
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value
    
class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['phone_number', 'name', 'email', 'role']
        read_only_fields = ['phone_number', 'role'] 

    def update(self, instance, validated_data):
        if 'first_name' in validated_data:
            instance.first_name = validated_data.pop('first_name')
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'complete_address', 'landmark', 'pincode', 'latitude', 'longitude', 'is_default']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)