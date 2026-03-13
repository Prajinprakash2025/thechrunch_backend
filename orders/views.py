from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.permissions import IsAdminOrStaff
from accounts.models import User, Address
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem, MenuItemVariant 
from .serializers import CartSerializer, OrderSerializer, AdminOrderSerializer
from rest_framework.pagination import PageNumberPagination
from notifications.utils import (
    send_telegram_order_notification, 
    send_telegram_cancellation_notification,
    send_fcm_notification
)
from notifications.models import AdminNotification

# ==========================================
# 1. CART MANAGEMENT APIs
# ==========================================

class CartDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        variant_id = request.data.get('variant_id') 
        action = request.data.get('action') 
        quantity = int(request.data.get('quantity', 1))

        if not item_id or not action:
            return Response({"error": "item_id and action are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu_item = get_object_or_404(MenuItem, id=item_id)
        
        variant = None
        if variant_id:
            variant = get_object_or_404(MenuItemVariant, id=variant_id, menu_item=menu_item)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=menu_item, variant=variant)
        
        if created:
            cart_item.quantity = 0 

        if action == 'add':
            cart_item.quantity += quantity
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > quantity:
                cart_item.quantity -= quantity
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(cart, context={'request': request})
        return Response({"message": f"Successfully performed {action}", "cart_data": serializer.data}, status=status.HTTP_200_OK)


class CartMergeView(views.APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items_data = request.data.get('items', [])

        if not items_data:
            return Response({"message": "No items to merge"}, status=status.HTTP_400_BAD_REQUEST)

        cart.items.all().delete()
        for data in items_data:
            item_id = data.get('item_id')
            variant_id = data.get('variant_id') 
            quantity = data.get('quantity', 1)
            
            menu_item = get_object_or_404(MenuItem, id=item_id)
            variant = MenuItemVariant.objects.filter(id=variant_id, menu_item=menu_item).first() if variant_id else None
            
            CartItem.objects.create(cart=cart, item=menu_item, variant=variant, quantity=quantity)

        serializer = CartSerializer(cart, context={'request': request})
        return Response({"status": True, "cart_data": serializer.data}, status=status.HTTP_200_OK)


# ==========================================
# 2. ORDER PLACEMENT
# ==========================================

class PlaceOrderView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic  
    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method', 'COD')
        delivery_address = get_object_or_404(Address, id=address_id, user=user)

        # 🌟 SAFETY: Using our fixed model property
        subtotal = sum(item.total_price for item in cart.items.all())

        order = Order.objects.create(
            user=user, delivery_address=delivery_address, subtotal=subtotal,
            delivery_fee=0, total_amount=subtotal, payment_method=payment_method,
            payment_status='PENDING', order_status='PLACED'
        )

        for cart_item in cart.items.all():
            # 🌟 SAFETY: Improved price logic to prevent NoneType error
            if cart_item.variant:
                price = cart_item.variant.offer_price if cart_item.variant.offer_price is not None else cart_item.variant.actual_price
            else:
                price = cart_item.item.offer_price if cart_item.item.offer_price is not None else cart_item.item.actual_price
            
            # Final fallback if admin forgot price
            price = price if price is not None else 0
                
            OrderItem.objects.create(
                order=order, 
                item=cart_item.item, 
                item_name=cart_item.item.name,
                size_name=cart_item.variant.size_name if cart_item.variant else None,
                price=price, 
                quantity=cart_item.quantity
            )
            
            # Inventory Management
            if cart_item.variant:
                cart_item.variant.quantity = max(0, cart_item.variant.quantity - cart_item.quantity)
                cart_item.variant.save()
            else:
                cart_item.item.quantity = max(0, cart_item.item.quantity - cart_item.quantity)
                cart_item.item.save() 

        cart.items.all().delete()

        # Notifications
        AdminNotification.objects.create(notification_type='order', message="New Order Received")
        
        try:
            send_telegram_order_notification(order)
        except: pass

        try:
            admin_staff_users = User.objects.filter(is_staff=True)
            for admin in admin_staff_users:
                send_fcm_notification(
                    user_id=admin.id,
                    title="New Order Received! 🍔",
                    body=f"Order #{order.id} from {order.user.first_name}. Total: ₹{order.total_amount}",
                    data={"order_id": str(order.id), "type": "NEW_ORDER"}
                )
        except: pass

        return Response({"message": "Order placed successfully!", "order_id": order.id}, status=status.HTTP_201_CREATED)


# ==========================================
# 3. USER ORDER HISTORY & CANCELLATION
# ==========================================

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class CancelOrderView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.order_status != 'PLACED':
            return Response({"error": "Cannot cancel processed order."}, status=status.HTTP_400_BAD_REQUEST)

        order.order_status = 'CANCELLED'
        order.cancelled_by = request.user
        order.save()

        # Return items to stock correctly
        for order_item in order.items.all():
            if order_item.item: 
                if order_item.size_name:
                    variant = MenuItemVariant.objects.filter(menu_item=order_item.item, size_name=order_item.size_name).first()
                    if variant:
                        variant.quantity += order_item.quantity
                        variant.save()
                else:
                    order_item.item.quantity += order_item.quantity
                    order_item.item.save()

        try:
            send_telegram_cancellation_notification(order)
        except: pass

        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)


# ==========================================
# 4. ADMIN DASHBOARD APIs
# ==========================================

class HistoryPagination(PageNumberPagination):
    page_size = 12  
    page_size_query_param = 'page_size'
    max_page_size = 50

class AdminOrderListView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = HistoryPagination 
    
    def get_queryset(self):
        status_param = self.request.query_params.get('status', None)
        search_order_id = self.request.query_params.get('order_id', None)
        
        if status_param == 'HISTORY':
            queryset = Order.objects.filter(
                order_status__in=['DELIVERED', 'CANCELLED']
            ).order_by('-updated_at')  
            
            if search_order_id:
                try:
                    queryset = queryset.filter(id=int(search_order_id))
                except ValueError:
                    queryset = queryset.none()
            return queryset
        
        queryset = Order.objects.all().order_by('created_at')
        if status_param:
            queryset = queryset.filter(order_status=status_param)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        status_param = request.query_params.get('status', None)

        if status_param == 'HISTORY':
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class AdminOrderStatusUpdateView(views.APIView):
    permission_classes = [IsAdminOrStaff]   
    
    @transaction.atomic
    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        
        if new_status == 'CANCELLED' and order.order_status != 'CANCELLED':
            order.cancelled_by = request.user
            for order_item in order.items.all():
                if order_item.item: 
                    if order_item.size_name:
                        variant = MenuItemVariant.objects.filter(menu_item=order_item.item, size_name=order_item.size_name).first()
                        if variant:
                            variant.quantity += order_item.quantity
                            variant.save()
                    else:
                        order_item.item.quantity += order_item.quantity
                        order_item.item.save()

        order.order_status = new_status
        order.save()
        return Response({"message": f"Order updated to {new_status}"}, status=status.HTTP_200_OK)
    

class AdminOrderStatsView(views.APIView):
    permission_classes = [IsAdminOrStaff] 

    def get(self, request):
        return Response({
            "new_orders": Order.objects.filter(order_status='PLACED').count(),
            "preparing": Order.objects.filter(order_status='PREPARING').count(),
            "on_the_way": Order.objects.filter(order_status='ON_THE_WAY').count(),
            "history": Order.objects.filter(order_status__in=['DELIVERED', 'CANCELLED']).count()
        }, status=status.HTTP_200_OK)