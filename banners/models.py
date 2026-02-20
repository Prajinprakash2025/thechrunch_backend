from django.db import models

class Banner(models.Model):
    desktop_image = models.ImageField(upload_to='banners/desktop/',max_length=500)
    mobile_image = models.ImageField(upload_to='banners/mobile/',max_length=500)
    headline = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    button_label = models.CharField(max_length=50)
    link_url = models.CharField(max_length=200)
    
    # To hide/show a banner without deleting it
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline