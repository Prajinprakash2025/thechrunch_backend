from rest_framework import serializers
from .models import TableBooking
from django.utils import timezone

class TableBookingSerializer(serializers.ModelSerializer): # 's' ഒഴിവാക്കി
    class Meta:
        model = TableBooking
        fields = '__all__'

    def validate(self, data):
        booking_date = data.get('date')
        booking_time = data.get('time')
        
        now = timezone.localtime(timezone.now())
        current_date = now.date()
        current_time = now.time()

        if booking_date < current_date:
            raise serializers.ValidationError({"date": "Bookings cannot be made for past dates."})

        if booking_date == current_date:
            if booking_time < current_time:
                raise serializers.ValidationError({"time": "Bookings cannot be made for past time today."})

        return data