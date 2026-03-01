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
    

