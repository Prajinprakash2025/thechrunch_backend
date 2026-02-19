from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random



class User(AbstractUser):

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("employee", "Employee"),
        ("customer", "Customer"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"



class PhoneOTP(models.Model):

    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
