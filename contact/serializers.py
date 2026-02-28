from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "full_name",
            "email",
            "subject",
            "message",
            "created_at",
            "reply_message",  
            "replied_at",
        ]
        read_only_fields = ["id", "created_at","replied_at"]
