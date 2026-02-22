from django.urls import path

from .views import (
    ContactCreateView,
    AdminContactListView,
    AdminContactDetailView,
    AdminContactDeleteView,
    AdminContactReplyView,
)

urlpatterns = [

    # Public
    path("contact/", ContactCreateView.as_view()),

    # Admin APIs
    path("admin/contacts/", AdminContactListView.as_view()),
    path("admin/contacts/<int:pk>/", AdminContactDetailView.as_view()),
    path("admin/contacts/<int:pk>/delete/", AdminContactDeleteView.as_view()),
    path("admin/contacts/<int:pk>/reply/", AdminContactReplyView.as_view()),
]
