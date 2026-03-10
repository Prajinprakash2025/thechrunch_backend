from django.shortcuts import render

# Create your views here.
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

        # Create a new record or update the existing token for the user
        device, created = FCMDevice.objects.update_or_create(
            user=request.user,
            defaults={'fcm_token': token}
        )

        if created:
            message = "FCM token saved successfully"
        else:
            message = "FCM token updated successfully"

        return Response({"message": message}, status=status.HTTP_200_OK)