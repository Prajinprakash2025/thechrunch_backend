from django.urls import path
from . import views

urlpatterns = [
    # Cart APIs
    path('cart/merge/', views.CartMergeView.as_view(), name='cart_merge'),
    # Order APIs
    path('place-order/', views.PlaceOrderView.as_view(), name='place-order'),
    path('history/', views.OrderListView.as_view(), name='order-history'),
]