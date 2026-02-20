from django.urls import path
from .views import BannerListView,BannerCreateView,BannerUpdateView,BannerDeleteView

urlpatterns = [
    path('all/', BannerListView.as_view(), name='banner-list'),
    path('add/', BannerCreateView.as_view(), name='banner-add'),
    path('edit/<int:pk>/', BannerUpdateView.as_view(), name='banner-edit'),
    path('delete/<int:pk>/', BannerDeleteView.as_view(), name='banner-delete'),
]