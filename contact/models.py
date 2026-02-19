from django.db import models




class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # To track when the message was sent

    def __str__(self):
        return f"{self.subject} - {self.full_name}"