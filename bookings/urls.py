from django.urls import path
from .views import BookingCreateView

urlpatterns = [
    path('book/', BookingCreateView.as_view(), name='book-table'),
]