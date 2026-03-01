from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random


# ============================================================
# CUSTOM USER MODEL
# ============================================================
class User(AbstractUser):
    """
    Custom User Model supporting:
    - Superadmin (Django's default)
    - Admin (Replaces Owner)
    - Staff (Replaces Employee)
    - User (Replaces Customer)
    """

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("user", "User"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    # Optional flags (useful later)
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.role if self.role else 'superadmin'}"


class PhoneOTP(models.Model):
    """
    Acts as the Temporary Store for OTPs and Unverified Registrations
    """
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    
    # Temp Data Storage
    name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Tracks the 24-hour data life
    otp_created_at = models.DateTimeField(auto_now=True) # Tracks the 2-minute OTP life
    is_verified = models.BooleanField(default=False)

    def is_otp_expired(self):
        return timezone.now() > self.otp_created_at + timezone.timedelta(minutes=2)

    def is_data_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save() # Note: auto_now on otp_created_at will automatically reset the 2-min clock!

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
    

# Add this at the bottom of accounts/models.py
class Address(models.Model):
    ADDRESS_TYPES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )
    
    # Links this address to a specific user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    # Address Details
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='Home')
    complete_address = models.TextField(help_text="House/Flat No., Building Name, Street")
    landmark = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    
    # Swiggy Model: GPS tracking
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 🌟 SWIGGY MAGIC: If this address is set as default, turn off 'is_default' for all other addresses of this user.
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} - {self.address_type} - {self.pincode}"