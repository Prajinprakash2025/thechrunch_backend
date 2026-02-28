from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator

# Phone number validation rule
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# -------------------------------
# Password Login Serializer
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
# Send OTP Serializer
# -------------------------------
class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[phone_regex], 
        max_length=15
    )


# -------------------------------
# Verify OTP Serializer
# -------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[phone_regex], 
        max_length=15
    )
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value
    


from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    # We create a custom 'name' field for the frontend to use
    name = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'name']

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        
        # Create the user object
        user = User(
            username=validated_data['phone_number'], # Use phone number as the required username
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            first_name=name, # Save the name into Django's default first_name field
            role='user'      # Default role for new customer signups
        )
        
        # Set an unusable password since they will log in with OTP
        user.set_unusable_password() 
        user.save()
        
        return user