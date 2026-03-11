from django.urls import path
from .views import SaveFCMTokenView, DeleteFCMTokenView, UnreadNotificationsView, MarkNotificationReadView

urlpatterns = [
    # Existing FCM URLs
    path('save-fcm-token/', SaveFCMTokenView.as_view(), name='save_fcm_token'),
    path('delete-fcm-token/', DeleteFCMTokenView.as_view(), name='delete_fcm_token'),
    
    # New Notification URLs
    path('unread/', UnreadNotificationsView.as_view(), name='unread_notifications'),
    path('mark-read/<str:notification_type>/', MarkNotificationReadView.as_view(), name='mark_read_notification'),
]