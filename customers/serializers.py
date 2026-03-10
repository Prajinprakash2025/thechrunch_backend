from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.models import Order # Make sure 'orders' app name and 'Order' model name are correct

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    # SerializerMethodField means this data is calculated by a function, not from database column
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Fields must match your Custom User Model exactly
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'is_blocked', 
            'date_joined', 
            'total_orders'
        ]

    def get_total_orders(self, obj):
        """
        This function counts all orders placed by this specific user.
        """
        try:
            return Order.objects.filter(user=obj).count()
        except Exception:
            return 0