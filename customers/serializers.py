from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # NOTE: Make sure 'phone_number' matches your exact field name in the User model
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'is_blocked', 'date_joined','total_orders']