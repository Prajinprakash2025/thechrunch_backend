from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem 
from accounts.serializers import AddressSerializer 

# ==========================================
# CART SERIALIZERS
# ==========================================
class CartItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id', read_only=True)
    name = serializers.CharField(source='item.name', read_only=True)
    image = serializers.ImageField(source='item.image', read_only=True) 
    
    # 🌟 NEW: Added Variant details (Size Name)
    size_name = serializers.CharField(source='variant.size_name', read_only=True)
    variant_id = serializers.IntegerField(source='variant.id', read_only=True, allow_null=True)
    
    # 🌟 UPDATED: These fields now dynamically pick price from Variant or Base Item
    actual_price = serializers.SerializerMethodField()
    offer_price = serializers.SerializerMethodField()
    total_price = serializers.ReadOnlyField() # Uses the @property from models.py

    class Meta:
        model = CartItem
        fields = [
            'id', 'item_id', 'variant_id', 'name', 'size_name', 'image', 
            'actual_price', 'offer_price', 'quantity', 'total_price'
        ]

    def get_actual_price(self, obj):
        return obj.variant.actual_price if obj.variant else obj.item.actual_price

    def get_offer_price(self, obj):
        return obj.variant.offer_price if obj.variant else obj.item.offer_price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'cart_total']

    def get_cart_total(self, obj):
        # 🌟 UPDATED: Cleaner calculation using the model property
        return sum(item.total_price for item in obj.items.all())


# ==========================================
# ORDER SERIALIZERS (Customer Side)
# ==========================================
class OrderItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='item.image', read_only=True)
    item_id = serializers.IntegerField(source='item.id', read_only=True)

    class Meta:
        model = OrderItem
        # 🌟 ADDED 'size_name' here so the customer receipt shows "Mandhi (Full)"
        fields = ['id', 'item_id', 'item_name', 'size_name', 'image', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = AddressSerializer(read_only=True) 
    cancelled_by_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'delivery_address', 'subtotal', 'delivery_fee', 'total_amount',
            'payment_method', 'payment_status', 'order_status', 'created_at', 
            'cancelled_by_display', 'items'
        ]

    def get_cancelled_by_display(self, obj):
        if obj.order_status == 'CANCELLED' and obj.cancelled_by:
            # If the customer cancelled their own order
            if obj.cancelled_by == obj.user:
                name = f"{obj.cancelled_by.first_name} {obj.cancelled_by.last_name}".strip()
                return name if name else obj.cancelled_by.username
            
            # Safely get the role even if it is None in the database
            role = getattr(obj.cancelled_by, 'role', None)
            role_name = role.lower() if role else ''
            
            if role_name == 'admin' or obj.cancelled_by.is_superuser:
                return "Admin"
            elif role_name == 'staff':
                return "Staff"
            else:
                return "Admin"
        return None


# ==========================================
# ADMIN SERIALIZERS (Dashboard Side)
# ==========================================
class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = AddressSerializer(read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.CharField(source='user.phone_number', read_only=True)
    cancelled_by_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_phone', 'delivery_address', 
            'subtotal', 'delivery_fee', 'total_amount', 
            'payment_method', 'payment_status', 'order_status', 
            'created_at', 'cancelled_by_display', 'items'
        ]

    def get_customer_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return "Unknown Customer"

    def get_cancelled_by_display(self, obj):
        if obj.order_status == 'CANCELLED' and obj.cancelled_by:
            if obj.cancelled_by == obj.user:
                name = f"{obj.cancelled_by.first_name} {obj.cancelled_by.last_name}".strip()
                return name if name else obj.cancelled_by.username
            
            role = getattr(obj.cancelled_by, 'role', None)
            role_name = role.lower() if role else ''
            
            if role_name == 'admin' or obj.cancelled_by.is_superuser:
                return "Admin"
            elif role_name == 'staff':
                return "Staff"
            else:
                return "Admin"
        return None