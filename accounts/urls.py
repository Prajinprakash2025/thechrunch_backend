from django.urls import path
from .views import LoginView, SendOTPView, VerifyOTPView

urlpatterns = [

    # Password login
    path("login/", LoginView.as_view()),

    # OTP login
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
]
