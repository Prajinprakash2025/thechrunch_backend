from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # CART APIs
    # ==========================================
    # 1. Get Cart (Page Load)
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    
    # 2. Update Single Item (+, -, Remove)
    path('cart/update/', views.CartUpdateView.as_view(), name='cart_update'),
    
    # 3. Merge LocalStorage on Login
    path('cart/merge/', views.CartMergeView.as_view(), name='cart_merge'),

    # ==========================================
    # ORDER APIs
    # ==========================================
    # 4. Place Final Order (Checkout)
    path('place-order/', views.PlaceOrderView.as_view(), name='place-order'),
    
    # 5. Order History (List past orders)
    path('history/', views.OrderListView.as_view(), name='order-history'),

    # 6. Cancel Order
    path('cancel/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel-order'),
]