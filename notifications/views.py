from rest_framework import views, status
from rest_framework.response import Response
from accounts.permissions import IsAdminOrStaff 
from .models import FCMDevice
from rest_framework.views import APIView
from .models import AdminNotification

# ==========================================
# 1. SAVE TOKEN 
# ==========================================
class SaveFCMTokenView(views.APIView):
    permission_classes = [IsAdminOrStaff] # <-- Changed here

    def post(self, request):
        token = request.data.get('fcm_token')

        if not token:
            return Response(
                {"error": "FCM token is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        FCMDevice.objects.filter(fcm_token=token).exclude(user=request.user).delete()

        device, created = FCMDevice.objects.update_or_create(
            user=request.user,
            defaults={'fcm_token': token}
        )

        message = "FCM token saved successfully" if created else "FCM token updated successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)

# ==========================================
# 2. DELETE TOKEN (Logout)
# ==========================================
class DeleteFCMTokenView(views.APIView):
    permission_classes = [IsAdminOrStaff] # <-- Changed here

    def post(self, request):
        deleted_count, _ = FCMDevice.objects.filter(user=request.user).delete()
        
        if deleted_count > 0:
            return Response({"message": "FCM token deleted successfully. Notifications stopped."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No FCM token found for this user."}, status=status.HTTP_200_OK)


# ==========================================
# FETCH UNREAD NOTIFICATIONS (Grouped)
# ==========================================
class UnreadNotificationsView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        types = ['order', 'booking', 'inbox']
        response_data = []

        for n_type in types:
            # Count unread notifications for each type
            count = AdminNotification.objects.filter(notification_type=n_type, is_read=False).count()
            
            if count > 0:
                # Dynamic message generation
                if n_type == 'order':
                    msg = f"{count} New order{'s' if count > 1 else ''} received"
                elif n_type == 'booking':
                    msg = f"{count} New booking{'s' if count > 1 else ''} received"
                else:
                    msg = f"{count} New message{'s' if count > 1 else ''} in inbox"

                response_data.append({
                    "id": n_type,  # Sending the type as ID makes marking it read easier
                    "type": n_type,
                    "message": msg,
                    "count": count
                })

        return Response(response_data, status=status.HTTP_200_OK)

# ==========================================
# MARK NOTIFICATIONS AS READ
# ==========================================
class MarkNotificationReadView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, notification_type):
        # Mark all unread notifications of that specific type as read
        notifications = AdminNotification.objects.filter(
            notification_type=notification_type, 
            is_read=False
        )
        
        updated_count = notifications.update(is_read=True)
        
        return Response({
            "status": "success", 
            "message": f"{updated_count} {notification_type} notification(s) marked as read"
        }, status=status.HTTP_200_OK)