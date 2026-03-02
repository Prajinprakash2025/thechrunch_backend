from rest_framework import serializers
from .models import SiteSetting

class SiteSettingSerializer(serializers.ModelSerializer):
    # Mapping: Frontend variables -> Backend fields
    appName = serializers.CharField(source='restaurant_name', required=False)
    email = serializers.EmailField(source='email_address', required=False)
    phone = serializers.CharField(source='phone_number', required=False)
    address = serializers.CharField(source='physical_address', required=False)
    location = serializers.CharField(source='map_link', allow_blank=True, required=False)
    deliveryRadius = serializers.IntegerField(source='delivery_radius', required=False)
    footerDescription = serializers.CharField(source='footer_description', allow_blank=True, required=False)

    # Fields for nested data (workingHours and socials)
    workingHours = serializers.DictField(child=serializers.CharField(allow_blank=True), write_only=True, required=False)
    socials = serializers.DictField(child=serializers.CharField(allow_blank=True), write_only=True, required=False)

    class Meta:
        model = SiteSetting
        fields = [
            'appName', 'email', 'phone', 'address', 'location', 
            'deliveryRadius', 'footerDescription', 'workingHours', 'socials'
        ]

    # Convert backend data to frontend React format (GET)
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['workingHours'] = {
            'weekdays': instance.working_hours_mon_sat,
            'sunday': instance.working_hours_sunday
        }
        data['socials'] = {
            'instagram': instance.instagram_url,
            'facebook': instance.facebook_url,
            'twitter': instance.twitter_url,
            'whatsapp': instance.whatsapp_url
        }
        return data

    # Map frontend data to backend fields and save (PUT/PATCH)
    def update(self, instance, validated_data):
        working_hours = validated_data.pop('workingHours', None)
        socials = validated_data.pop('socials', None)

        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update nested fields
        if working_hours:
            instance.working_hours_mon_sat = working_hours.get('weekdays', instance.working_hours_mon_sat)
            instance.working_hours_sunday = working_hours.get('sunday', instance.working_hours_sunday)

        if socials:
            instance.instagram_url = socials.get('instagram', instance.instagram_url)
            instance.facebook_url = socials.get('facebook', instance.facebook_url)
            instance.twitter_url = socials.get('twitter', instance.twitter_url)
            instance.whatsapp_url = socials.get('whatsapp', instance.whatsapp_url)

        instance.save()
        return instance