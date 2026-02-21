from django.urls import path
from .views import LoginView, SendOTPView, VerifyOTPView, CreateStaffView,VerifySessionView

urlpatterns = [
    # Password login
    path("login/", LoginView.as_view(), name="login"),

    # OTP login
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/verify-session/", VerifySessionView.as_view()),


    # Admin creating a new staff account
    path("create-staff/", CreateStaffView.as_view(), name="create-staff"),
]