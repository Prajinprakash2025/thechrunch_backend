from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # CART APIs
    # ==========================================
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/update/', views.CartUpdateView.as_view(), name='cart_update'),
    path('cart/merge/', views.CartMergeView.as_view(), name='cart_merge'),

    # ==========================================
    # ORDER APIs (User)
    # ==========================================
    path('place-order/', views.PlaceOrderView.as_view(), name='place-order'),
    path('history/', views.OrderListView.as_view(), name='order-history'),
    path('cancel/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel-order'),

    # ==========================================
    # ORDER APIs (Admin Kitchen Dashboard)
    # ==========================================
    # GET /api/orders/admin/?status=PLACED
    path('admin/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    
    # PATCH /api/orders/admin/<order_id>/status/
    path('admin/<int:order_id>/status/', views.AdminOrderStatusUpdateView.as_view(), name='admin-order-status-update'),
]