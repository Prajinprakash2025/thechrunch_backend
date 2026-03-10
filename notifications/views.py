from rest_framework import views, status
from rest_framework.response import Response
from accounts.permissions import IsAdminOrStaff 
from .models import FCMDevice

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