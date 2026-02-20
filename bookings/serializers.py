from rest_framework import serializers
from django.utils import timezone
from .models import TableBooking

class TableBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableBooking
        fields = '__all__'

    def validate(self, data):
        booking_date = data.get('date')
        booking_time = data.get('time')

        # Get current local date and time
        now = timezone.localtime(timezone.now())
        current_date = now.date()
        current_time = now.time()

        if booking_date and booking_date < current_date:
            raise serializers.ValidationError({"date": "Bookings cannot be made for past dates."})

        if booking_date == current_date and booking_time:
            if booking_time < current_time:
                raise serializers.ValidationError({"time": "Bookings cannot be made for past time today."})

        return data