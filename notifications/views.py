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

        # Look for the exact token first. 
        # If it exists, update the user to the current logged-in user.
        # If it does not exist, create a new record.
        device, created = FCMDevice.objects.update_or_create(
            fcm_token=token,
            defaults={'user': request.user}
        )

        if created:
            message = "FCM token saved successfully"
        else:
            message = "FCM token updated successfully"

        return Response({"message": message}, status=status.HTTP_200_OK)