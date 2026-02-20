from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            'id', 
            'desktop_image', 
            'mobile_image', 
            'headline', 
            'description', 
            'button_label', 
            'link_url'
        ]