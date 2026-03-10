from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.models import Order # Make sure 'orders' is the app name

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    # SerializerMethodField means it's a custom field not in the User model
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        # These are the fields sent to your frontend dashboard
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
        Calculates the total number of orders placed by this user.
        """
        try:
            # Matches the 'user' field in your Order model
            return Order.objects.filter(user=obj).count()
        except Exception:
            return 0