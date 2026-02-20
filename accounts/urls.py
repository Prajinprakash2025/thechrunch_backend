from django.urls import path
from .views import LoginView, SendOTPView, VerifyOTPView, CreateStaffView

urlpatterns = [
    # Password login
    path("login/", LoginView.as_view(), name="login"),

    # OTP login
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    # Admin creating a new staff account
    path("create-staff/", CreateStaffView.as_view(), name="create-staff"),
]