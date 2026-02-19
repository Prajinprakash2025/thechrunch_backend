from django.urls import path
from .views import LoginView, SendOTPView, VerifyOTPView,CreateEmployeeView

urlpatterns = [

    # Password login
    path("login/", LoginView.as_view()),

    # OTP login
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),

    path("create-employee/", CreateEmployeeView.as_view()),
]
