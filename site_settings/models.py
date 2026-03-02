from django.db import models

class SiteSetting(models.Model):
    # --- Contact & Location ---
    restaurant_name = models.CharField(max_length=255, blank=True, null=True, default="")
    email_address = models.EmailField(blank=True, null=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, null=True, default="")
    physical_address = models.TextField(blank=True, null=True, default="")
    map_link = models.URLField(max_length=500, blank=True, null=True)
    delivery_radius = models.PositiveIntegerField(default=0, help_text="In KM")

    # --- Footer Content & Hours ---
    footer_description = models.TextField(blank=True, null=True, default="")
    working_hours_mon_sat = models.CharField(max_length=100, blank=True, null=True, default="")
    working_hours_sunday = models.CharField(max_length=100, blank=True, null=True, default="")

    # --- Social Media Links ---
    instagram_url = models.URLField(max_length=500, blank=True, null=True)
    facebook_url = models.URLField(max_length=500, blank=True, null=True)
    twitter_url = models.URLField(max_length=500, blank=True, null=True)
    whatsapp_url = models.URLField(max_length=500, blank=True, null=True)

    # Singleton Pattern: Ensure only one row is ever created
    def save(self, *args, **kwargs):
        self.pk = 1 
        super(SiteSetting, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Website Settings"