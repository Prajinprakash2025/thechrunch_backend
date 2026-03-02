from django.urls import path
from . import views

urlpatterns = [
    path('info/', views.SiteSettingRetrieveUpdateView.as_view(), name='site-settings'),
]