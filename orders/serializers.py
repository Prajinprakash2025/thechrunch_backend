from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from accounts.serializers import AddressSerializer # To show address details in order

# ==========================================
# CART SERIALIZERS
# ==========================================
# ==========================================
# CART SERIALIZERS
# ==========================================
class CartItemSerializer(serializers.ModelSerializer):
    # 🌟 FIX: Renamed fields to match what React expects!
    item_id = serializers.IntegerField(source='item.id', read_only=True)
    name = serializers.CharField(source='item.name', read_only=True)
    image = serializers.ImageField(source='item.image', read_only=True)
    actual_price = serializers.DecimalField(source='item.actual_price', max_digits=10, decimal_places=2, read_only=True)
    offer_price = serializers.DecimalField(source='item.offer_price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        # 🌟 FIX: Updated the fields list here too!
        fields = ['id', 'item_id', 'name', 'image', 'actual_price', 'offer_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        price = obj.item.offer_price if obj.item.offer_price else obj.item.actual_price
        return price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'cart_total']

    # 🌟 FIX: Safely calculate the grand total using the same logic
    def get_cart_total(self, obj):
        total = 0
        for cart_item in obj.items.all():
            price = cart_item.item.offer_price if cart_item.item.offer_price else cart_item.item.actual_price
            total += (price * cart_item.quantity)
        return total


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