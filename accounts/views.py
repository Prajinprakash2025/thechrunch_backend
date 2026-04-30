from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils import timezone
from .models import PhoneOTP, Address
from .serializers import (
    LoginSerializer, SendOTPSerializer, VerifyOTPSerializer, 
    UserProfileSerializer, AddressSerializer
)
from .utils import send_sms_otp
from .permissions import IsAdminOrStaff
from .authentication import get_tokens_for_user
from .utils import send_sms_otp

User = get_user_model()

# ============================================================================
# 🛡️ GLOBAL COOKIE SETTINGS (Production Standard)
# ============================================================================
def get_cookie_params():
    """Centralized cookie parameters to avoid mismatch during set/delete"""
    return {
        'httponly': True,
        'secure': True,      # Production-il HTTPS nirbandham!
        'samesite': 'None',  # Cross-domain support
        'path': '/'
    }

def set_jwt_cookies(response, user):
    """Generates and sets JWT tokens in cookies"""
    refresh = RefreshToken.for_user(user)
    cookie_params = get_cookie_params()
    
    response.set_cookie(key='access_token', value=str(refresh.access_token), max_age=3600, **cookie_params)
    response.set_cookie(key='refresh_token', value=str(refresh), max_age=3600 * 24 * 7, **cookie_params)
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
        return Response({"status": True, "message": "Staff member created successfully."}, status=status.HTTP_201_CREATED)

# ============================================================================
# 2. OTP FLOW: SIGNUP & LOGIN
# ============================================================================
def check_otp_cooldown(phone):
    try:
        otp_instance = PhoneOTP.objects.get(phone_number=phone)
        time_diff = (timezone.now() - otp_instance.otp_created_at).total_seconds()
        if time_diff < 60:
            return int(60 - time_diff)
    except PhoneOTP.DoesNotExist:
        pass
    return 0

class SignupRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("name")
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if not all([name, email, phone]):
            return Response({"status": False, "message": "Name, Email, and Phone are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        user = User.objects.filter(phone_number=phone).first()
        
        # 🟢 FIX 1: If user exists and IS VERIFIED, block them.
        if user and user.is_active:
            return Response({"status": False, "message": "User already exists. Please Login."}, status=status.HTTP_400_BAD_REQUEST)

        # 🌟 COOLDOWN CHECK
        cooldown = check_otp_cooldown(phone)
        if cooldown > 0:
            return Response({
                "status": False,
                "message": f"Please wait {cooldown} seconds before requesting a new OTP.",
                "resend_delay": cooldown
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 🟢 FIX 2: If user exists but is NOT VERIFIED (is_active=False), just update details instead of throwing error
        if user and not user.is_active:
            user.first_name = name
            user.email = email
            user.save()
        else:
            # Create a TEMPORARY/UNVERIFIED user
            User.objects.create(username=phone, phone_number=phone, first_name=name, email=email, is_active=False, role="user")

        # Generate and Send OTP
        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        send_sms_otp(phone, otp_instance.otp)

        return Response({
            "status": True, 
            "message": "f"Your OTP is {otp_instance.otp}", 
            "resend_delay": 60
        }, status=status.HTTP_200_OK)
    

class LoginRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        
        user = User.objects.filter(phone_number=phone).first()

        # 🟢 FIX 4: Prevent unverified users from logging in
        if not user or not user.is_active:
            return Response({"status": False, "message": "Account not found or not verified. Please Register first."}, status=status.HTTP_404_NOT_FOUND)

        # 🌟 COOLDOWN CHECK
        cooldown = check_otp_cooldown(phone)
        if cooldown > 0:
            return Response({
                "status": False,
                "message": f"Please wait {cooldown} seconds before requesting a new OTP.",
                "resend_delay": cooldown
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate and Send OTP
        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        send_sms_otp(phone, otp_instance.otp)
        
        return Response({
            "status": True, 
            "message": "f"Your OTP is {otp_instance.otp}", 
            "resend_delay": 60
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get("phone_number")
        if not phone:
            return Response({"status": False, "message": "Phone number required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 🌟 COOLDOWN CHECK
        cooldown = check_otp_cooldown(phone)
        if cooldown > 0:
            return Response({
                "status": False,
                "message": f"Please wait {cooldown} seconds before requesting a new OTP.",
                "resend_delay": cooldown
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate and Send OTP
        otp_instance, _ = PhoneOTP.objects.get_or_create(phone_number=phone)
        otp_instance.generate_otp()
        send_sms_otp(phone, otp_instance.otp)
        
        # 🌟 RETURN OTP IN RESPONSE (For Frontend Toast & Debugging)
        return Response({
            "status": True, 
            "message": f"Your OTP is {otp_instance.otp}", 
            "otp": otp_instance.otp, 
            "resend_delay": 60
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        otp = request.data.get("otp")

        if not phone or not otp:
            return Response({"status": False, "message": "Phone number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        try:
            otp_instance = PhoneOTP.objects.get(phone_number=phone)
            if otp_instance.otp != str(otp):
                return Response({"status": False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneOTP.DoesNotExist:
            return Response({"status": False, "message": "OTP not found for this number"}, status=status.HTTP_404_NOT_FOUND)

        # Find the User
        user = User.objects.filter(phone_number=phone).first()
        if not user:
            return Response({"status": False, "message": "User details not found"}, status=status.HTTP_404_NOT_FOUND)

        # 🟢 FIX 3: Activate account ONLY upon successful OTP verification
        if not user.is_active:
            user.is_active = True
            user.save()

        # Generate Tokens
        tokens = get_tokens_for_user(user)

        # Prepare Response
        response = Response({
            "status": True, 
            "message": "Verification Successful", 
            "name": user.first_name,
            "role": user.role
        }, status=status.HTTP_200_OK)

        # Set Cookies (Important for Auth)
        response.set_cookie(
            key='access_token',
            value=tokens['access'],
            httponly=True,
            samesite='None',
            secure=True, 
            max_age=15 * 60 # 15 minutes
        )
        response.set_cookie(
            key='refresh_token',
            value=tokens['refresh'],
            httponly=True,
            samesite='None',
            secure=True,
            max_age=7 * 24 * 60 * 60 # 7 days
        )

        return response
# ============================================================================
# 3. SESSION UTILITIES (Refresh & Logout)
# ============================================================================
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
            
            cookie_params = get_cookie_params()
            response.set_cookie(key='access_token', value=str(refresh.access_token), max_age=3600, **cookie_params)
            return response

        except (TokenError, InvalidToken, User.DoesNotExist):
            response = Response({"status": False, "error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
            cookie_params = get_cookie_params()
            
            # 🛠️ FIX: TypeError ഒഴിവാക്കാൻ delete_cookie-ക്ക് പകരം set_cookie ഉപയോഗിച്ച് expire ആക്കുന്നു
            response.set_cookie('access_token', '', max_age=0, expires='Thu, 01 Jan 1970 00:00:00 GMT', **cookie_params)
            response.set_cookie('refresh_token', '', max_age=0, expires='Thu, 01 Jan 1970 00:00:00 GMT', **cookie_params)
            return response

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({
            "status": True,
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

        cookie_params = get_cookie_params()
        
        # 🛠️ FIX: TypeError ഒഴിവാക്കാൻ delete_cookie ഉപയോഗിക്കുന്നില്ല. 
        # പകരം ഒറിജിനൽ പാരാമീറ്ററുകൾ വെച്ച് തന്നെ കുക്കി Force Expire ചെയ്യുന്നു.
        response.set_cookie('access_token', '', max_age=0, expires='Thu, 01 Jan 1970 00:00:00 GMT', **cookie_params)
        response.set_cookie('refresh_token', '', max_age=0, expires='Thu, 01 Jan 1970 00:00:00 GMT', **cookie_params)

        return response

# ============================================================================
# 4. PROFILE & ADDRESS MANAGEMENT
# ============================================================================
class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        assigned_role = user.role
        if not assigned_role and user.is_superuser:
            assigned_role = "admin"
            
        display_name = user.first_name if user.first_name else user.username

        return Response({
            "status": True,
            "is_authenticated": True,
            "user": {
                "id": user.id,
                "role": assigned_role,
                "name": display_name,
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

    def patch(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response({"status": False, "message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Address updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response({"status": False, "message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
            
        address.delete()
        return Response({"status": True, "message": "Address deleted"}, status=status.HTTP_200_OK)