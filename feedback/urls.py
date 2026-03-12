from django.urls import path
from .views import ReviewEligibilityCheckView, ReviewCreateView, ReviewListView

urlpatterns = [
    path('eligibility/', ReviewEligibilityCheckView.as_view(), name='review-eligibility'),
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    path('list/', ReviewListView.as_view(), name='review-list'),
]