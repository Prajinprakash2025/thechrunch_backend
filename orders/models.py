from django.db import models
from django.conf import settings
from inventory.models import MenuItem 
from accounts.models import Address   

# ==========================================
# 1. CART MODELS (For Step 1: Cart)
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
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
        
    @property
    def total_price(self):
        # Calculate total price based on offer price if available, else actual price
        price = self.item.offer_price if self.item.offer_price else self.item.actual_price
        return price * self.quantity

# ==========================================
# 2. ORDER MODELS (For Step 2 & 3: Checkout)
# ==========================================

class Order(models.Model):
    # --- Enums for Status ---
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
    

    # --- Core Order Info ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- Bill Details ---
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    # --- Status & Payment ---
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PLACED')

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.first_name} - {self.order_status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    
    # Save explicitly to keep history intact even if menu item price changes later
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item_name} (Order #{self.order.id})"