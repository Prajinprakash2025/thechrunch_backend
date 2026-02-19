from django.db import models

# Create your models here.

class TableBooking(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)  # Optional
    date = models.DateField()
    time = models.TimeField()
    guests = models.CharField(max_length=50) 
    notes = models.TextField(blank=True, null=True)   # Optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.date} {self.time}"