from django.urls import path
from .views import BookingCreateView

urlpatterns = [
    path('create/', BookingCreateView.as_view(), name='book-table'),
]