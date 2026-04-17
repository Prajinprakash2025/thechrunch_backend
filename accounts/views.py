from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import PhoneOTP, Address
from .serializers import (
    LoginSerializer, SendOTPSerializer, VerifyOTPSerializer, 
    UserProfileSerializer, AddressSerializer
)
from .utils import send_sms_otp
from .permissions import IsAdminOrStaff

User = get_user_model()

# ============================================================================
# HELPER FUNCTION: To set Token in HTTP-Only Cookie
# ============================================================================
def set_jwt_cookies(response, user):
    """Generates JWT and attaches BOTH access and refresh tokens as HTTP-Only cookies"""
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh) # 🌟 NEW: Get the refresh token string
    
    # 1. Set Access Token Cookie
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,   
        secure=False,     # ⚠️ Set to True for Production (HTTPS). False for local HTTP testing.
        samesite='None', 
        max_age=3600 * 24 * 7 # 7 Days expiry
    )
    
    # 2. Set Refresh Token Cookie (🌟 NEW)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,   
        secure=False,     # ⚠️ Set to True for Production (HTTPS).
        samesite='None', 
        max_age=3600 * 24 * 30 # 30 Days expiry for refresh token
    )
    
    return response

# ============================================================================
# 1. ADMIN & STAFF (Password Login)
# ============================================================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            
            response_data = {
                "status": True,
                "message": "Login successful",
                "role": user.role,
                "user_id": user.id,
                "name": user.first_name,
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            return set_jwt_cookies(response, user)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# CREATE STAFF VIEW (With Permissions)
class CreateStaffView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        return Response({
            "status": True,
            "message": "Staff member created successfully."
        }, status=status.HTTP_201_CREATED)

# ============================================================================
# 2. OTP FLOW: SIGNUP & LOGIN
# ============================================================================
class BaseSendOTPView(APIView):
    permission_classes = [AllowAny]

    def process_otp_request(self, request, is_login=False):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        user_exists = User.objects.filter(phone_number=phone).exists()

        if is_login and not user_exists:
            return Response({"status": False, "message": "Phone number not registered. Please sign up."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not is_login and user_exists:
            return Response({"status": False, "message": "Phone number already registered. Please login."}, status=status.HTTP_400_BAD_REQUEST)

        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        
        if not getattr(settings, 'TESTING', False):
             send_sms_otp(phone, otp_instance.otp)

        return Response({"status": True, "message": "OTP sent successfully!"}, status=status.HTTP_200_OK)

class SignupRequestOTPView(BaseSendOTPView):
    def post(self, request):
        return self.process_otp_request(request, is_login=False)

class LoginRequestOTPView(BaseSendOTPView):
    def post(self, request):
        return self.process_otp_request(request, is_login=True)

class ResendOTPView(BaseSendOTPView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        user_exists = User.objects.filter(phone_number=phone).exists()
        return self.process_otp_request(request, is_login=user_exists)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]
        name = serializer.validated_data.get("name", "")
        email = serializer.validated_data.get("email", "")

        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone, otp=otp)
        except PhoneOTP.DoesNotExist:
            return Response({"status": False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        if otp_instance.is_otp_expired():
            return Response({"status": False, "message": "OTP expired. Please click resend."}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={
                "username": phone,
                "first_name": name, 
                "email": email, 
                "role": "user",
                "is_phone_verified": True
            }
        )

        if not created and not user.is_active:
            return Response({"status": False, "message": "Account disabled."}, status=status.HTTP_400_BAD_REQUEST)

        otp_instance.delete()

        response_data = {
            "status": True,
            "message": "Verification successful!",
            "is_new_user": created,
            "role": user.role,
            "name": user.first_name,
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        return set_jwt_cookies(response, user)

# ============================================================================
# 3. LOGOUT (Clears BOTH Cookies)
# ============================================================================
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"status": True, "message": "Logged out successfully"}, status=status.HTTP_200_OK)
        # 🌟 NEW: Delete both access and refresh cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

# ============================================================================
# 4. PROFILE & SESSION
# ============================================================================
class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # 🛠️ FIX: User oru superuser aanu, pakshe role empty aanengil athu "admin" aakki kanikkanam
        assigned_role = user.role
        if not assigned_role and user.is_superuser:
            assigned_role = "admin"
            
        # 🛠️ FIX: First name empty aanengil username (eg: 'admin') kanikkanam
        display_name = user.first_name if user.first_name else user.username

        return Response({
            "status": True,
            "is_authenticated": True,
            "user": {
                "id": user.id,
                "role": assigned_role,       # Updated role
                "name": display_name,        # Updated name
                "phone_number": user.phone_number
            }
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Profile updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# 5. ADDRESS MANAGEMENT
# ============================================================================
class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-id')
        serializer = AddressSerializer(addresses, many=True)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Address added", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Address.objects.get(pk=pk, user=user)
        except Address.DoesNotExist:
            return None

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response({"status": False, "message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
            
        address.delete()
        return Response({"status": True, "message": "Address deleted"}, status=status.HTTP_200_OK)