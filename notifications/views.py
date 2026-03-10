from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FCMDevice

class SaveFCMTokenView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('fcm_token')

        if not token:
            return Response({"error": "FCM token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove token if it belongs to another user
        FCMDevice.objects.filter(fcm_token=token).exclude(user=request.user).delete()

        # Update or create for the current user (Fixed request.user)
        device, created = FCMDevice.objects.update_or_create(
            user=request.user,
            defaults={'fcm_token': token}
        )

        message = "FCM token saved successfully" if created else "FCM token updated successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)