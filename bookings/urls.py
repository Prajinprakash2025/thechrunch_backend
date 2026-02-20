from django.urls import path
from .views import CreateBookingView,ListBookingsView

urlpatterns = [
path('create/', CreateBookingView.as_view(), name='book-table'),#user can book
path('all/', ListBookingsView.as_view(), name='list-bookings'),#admin and staff can see
]