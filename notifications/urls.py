# notifications/urls.py
from django.urls import path
from .views import SaveFCMTokenView, DeleteFCMTokenView # Randum import cheyyanam

urlpatterns = [
    path('save-fcm-token/', SaveFCMTokenView.as_view(), name='save_fcm_token'),
    path('delete-fcm-token/', DeleteFCMTokenView.as_view(), name='delete_fcm_token'), # Ithu add cheyyuka
]