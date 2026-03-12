from django.urls import path
from .views import (
    ReviewEligibilityCheckView, ReviewCreateView, ReviewListView,
    AdminReviewListView, AdminReviewUpdateView # <-- Ithu puthiyath
)

urlpatterns = [
    # User APIs
    path('eligibility/', ReviewEligibilityCheckView.as_view(), name='review-eligibility'),
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    path('list/', ReviewListView.as_view(), name='review-list'),

    # Admin APIs
    path('admin/list/', AdminReviewListView.as_view(), name='admin-review-list'),
    path('admin/<int:pk>/update/', AdminReviewUpdateView.as_view(), name='admin-review-update'),
]