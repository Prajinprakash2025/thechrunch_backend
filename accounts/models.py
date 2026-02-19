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
    - Superadmin
    - Owner
    - Employee
    - Customer
    """

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("employee", "Employee"),
        ("customer", "Customer"),
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
    Handles OTP authentication for customers
    """

    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    # -------------------------------
    # OTP expiry check (5 mins)
    # -------------------------------
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    # -------------------------------
    # Generate OTP
    # -------------------------------
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))

        # Reset timestamp on regeneration
        self.created_at = timezone.now()

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
