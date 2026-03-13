from django.db import models
from django.conf import settings
from inventory.models import MenuItem, MenuItemVariant 
from accounts.models import Address   

# ==========================================
# 1. CART MODELS
# ==========================================
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.first_name}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    variant = models.ForeignKey(MenuItemVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        size_info = f" ({self.variant.size_name})" if self.variant else ""
        return f"{self.quantity} x {self.item.name}{size_info}"
        
    @property
    def total_price(self):
        # 🌟 SAFE LOGIC: This prevents the 'NoneType' Error
        if self.variant:
            price = self.variant.offer_price if self.variant.offer_price is not None else self.variant.actual_price
        else:
            price = self.item.offer_price if self.item.offer_price is not None else self.item.actual_price
        
        # If both prices are missing in admin, default to 0 to prevent crash
        if price is None:
            price = 0
            
        return price * self.quantity

# ==========================================
# 2. ORDER MODELS
# ==========================================
class Order(models.Model):
    # Removed Razorpay as requested
    PAYMENT_METHODS = (
        ('COD', 'Cash on Delivery'),
    )
    
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    ORDER_STATUS = (
        ('PLACED', 'Order Placed'),
        ('PREPARING', 'Preparing'),
        ('ON_THE_WAY', 'On the Way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_orders')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PLACED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=255)
    size_name = models.CharField(max_length=50, null=True, blank=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item_name} ({self.size_name}) - Order #{self.order.id}"