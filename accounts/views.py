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
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

# ============================================================================
# HELPER FUNCTION: To set Token in HTTP-Only Cookie
# ============================================================================
def set_jwt_cookies(response, user):
    """Generates Access & Refresh tokens and sets them as HTTP-Only Cookies"""
    refresh = RefreshToken.for_user(user)
    
    cookie_params = {
        'httponly': True,
        'secure': True,  # ⚠️ Production-il (HTTPS) True aakkanam
        'samesite': 'None',
        'max_age': 3600 * 24 * 7 # 7 Days
    }
    
    response.set_cookie(key='access_token', value=str(refresh.access_token), **cookie_params)
    response.set_cookie(key='refresh_token', value=str(refresh), **cookie_params)
    return response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"status": False, "error": "No refresh token found"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get('user_id')
            user = User.objects.get(id=user_id)

            response = Response({"status": True, "message": "Token refreshed successfully"}, status=status.HTTP_200_OK)

            # --- Cookie Parameters (Production Standard) ---
            cookie_params = {
                'httponly': True,
                'secure': True,      # Production-il HTTPS nirbandham
                'samesite': 'None',  # Cross-site work cheyyan
                'path': '/',         # Ella path-ilum cookie kittaam
            }

            # 1. New Access Token set cheyyunnu
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                max_age=3600, # 1 Hour
                **cookie_params
            )

            # 💡 OPTIONAL: Ninte settings-il Rotation ON aanengil puthiya refresh token koodi set cheyyunnam
            # response.set_cookie(
            #     key='refresh_token',
            #     value=str(refresh),
            #     max_age=86400 * 7, # 7 Days
            #     **cookie_params
            # )

            return response

        except (TokenError, InvalidToken, User.DoesNotExist):
            response = Response({"status": False, "error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
            # Cookie clear cheyyumpozhum same params (samesite, secure) venam!
            response.delete_cookie('access_token', samesite='None', secure=True)
            response.delete_cookie('refresh_token', samesite='None', secure=True)
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
            response = Response({
                "status": True,
                "message": "Login successful",
                "role": user.role or "admin",
                "name": user.first_name,
            }, status=status.HTTP_200_OK)
            return set_jwt_cookies(response, user)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateStaffView(APIView):
    permission_classes = [IsAdminOrStaff]
    def post(self, request):
        # Staff creation logic ivide add cheyyam
        return Response({"status": True, "message": "Staff member created successfully."}, status=201)

# ============================================================================
# 2. OTP FLOW: SIGNUP & LOGIN
# ============================================================================

class SignupRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if not all([name, email, phone]):
            return Response({"status": False, "message": "Name, Email, and Phone are required"}, status=400)

        if User.objects.filter(phone_number=phone).exists():
            return Response({"status": False, "message": "User already exists. Please Login."}, status=400)

        # Inactive user create cheyyunnu
        User.objects.create(
            username=phone,
            phone_number=phone,
            first_name=name,
            email=email,
            is_active=False,
            role="user"
        )

        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        send_sms_otp(phone, otp_instance.otp)

        return Response({
            "status": True, "message": "OTP sent!", "otp": otp_instance.otp 
        }, status=200)

class LoginRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        try:
            user = User.objects.get(phone_number=phone)
            otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
            otp_instance.generate_otp()
            send_sms_otp(phone, otp_instance.otp)
            return Response({"status": True, "message": "Login OTP sent!", "otp": otp_instance.otp}, status=200)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not registered."}, status=404)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone = request.data.get("phone_number")
        if not phone:
            return Response({"status": False, "message": "Phone number required"}, status=400)
        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        send_sms_otp(phone, otp_instance.otp)
        return Response({"status": True, "message": "OTP Resent!", "otp": otp_instance.otp}, status=200)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        otp = request.data.get("otp")

        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone, otp=otp)
            user = User.objects.get(phone_number=phone)
            
            user.is_active = True
            user.is_phone_verified = True
            user.save()
            
            otp_instance.delete()
            response = Response({"status": True, "message": "Login Successful", "name": user.first_name}, status=200)
            return set_jwt_cookies(response, user)
        except (PhoneOTP.DoesNotExist, User.DoesNotExist):
            return Response({"status": False, "message": "Invalid OTP or Phone Number"}, status=400)

# ============================================================================
# 3. LOGOUT (Clears BOTH Cookies)
# ============================================================================
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({
            "status": True, 
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

        # 🛠️ Same parameters used during login/refresh
        cookie_params = {
            'httponly': True,
            'secure': True,      # Production-il HTTPS aanennu urappakkuka
            'samesite': 'None',
        }

        # Clear Access Token
        response.delete_cookie('access_token', **cookie_params)
        # Clear Refresh Token
        response.delete_cookie('refresh_token', **cookie_params)

        # 💡 Extra Safety: Max Age 0 set cheyyunnathu nallathaanu
        # response.set_cookie('access_token', '', max_age=0, **cookie_params)
        
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