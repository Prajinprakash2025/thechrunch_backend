from django.urls import path
from . import views

urlpatterns = [
    # Cart APIs
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/update/', views.CartUpdateView.as_view(), name='cart-update'),
    
    # Order APIs
    path('place-order/', views.PlaceOrderView.as_view(), name='place-order'),
    path('history/', views.OrderListView.as_view(), name='order-history'),
]