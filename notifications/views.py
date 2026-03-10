from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FCMDevice

class SaveFCMTokenView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('fcm_token')

        if not token:
            return Response(
                {"error": "FCM token is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Remove this token if it exists for any other user
        FCMDevice.objects.filter(fcm_token=token).exclude(user=request.user).delete()

        # 2. Update or create the token for the current logged-in user
        device, created = FCMDevice.objects.update_or_create(
            user=request.user,
            defaults={'fcm_token': token}
        )

        message = "FCM token saved successfully" if created else "FCM token updated successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)