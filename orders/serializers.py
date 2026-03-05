from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from accounts.serializers import AddressSerializer # To show address details in order

# ==========================================
# CART SERIALIZERS
# ==========================================
class CartItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_image = serializers.ImageField(source='item.image', read_only=True)
    actual_price = serializers.DecimalField(source='item.actual_price', max_digits=10, decimal_places=2, read_only=True)
    offer_price = serializers.DecimalField(source='item.offer_price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'item_id', 'item_name', 'item_image', 'actual_price', 'offer_price', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'cart_total']

    def get_cart_total(self, obj):
        return sum(item.total_price for item in obj.items.all())

# ==========================================
# ORDER SERIALIZERS
# ==========================================
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'item_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # This will return the full address details instead of just the ID
    delivery_address = AddressSerializer(read_only=True) 

    class Meta:
        model = Order
        fields = [
            'id', 'delivery_address', 'subtotal', 'delivery_fee', 'total_amount',
            'payment_method', 'payment_status', 'order_status', 'created_at', 'items'
        ]