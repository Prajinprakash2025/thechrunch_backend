from django.urls import path
from .views import (
    LoginView, 
    SignupRequestOTPView, 
    ResendOTPView,
    VerifyOTPView, 
    LoginRequestOTPView,
    CreateStaffView,
    VerifySessionView,
    LogoutView,
    UserProfileView
)

urlpatterns = [
    # ==========================================
    # 1. ADMIN & STAFF (Password)
    # ==========================================
    path('admin-login/', LoginView.as_view(), name='admin_login'),
    path('create-staff/', CreateStaffView.as_view(), name='create_staff'),

    # ==========================================
    # 2. USER OTP FLOW (Signup & Login)
    # ==========================================
    path('register/', SignupRequestOTPView.as_view(), name='register_request_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login-otp/', LoginRequestOTPView.as_view(), name='login_request_otp'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),

    # ==========================================
    # 3. SESSION UTILITIES
    # ==========================================
    path('verify-session/', VerifySessionView.as_view(), name='verify_session'),
    path('logout/', LogoutView.as_view(), name='logout'),
]