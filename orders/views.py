from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.permissions import IsAdminOrStaff
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem 
from accounts.models import Address
from .serializers import CartSerializer, OrderSerializer, AdminOrderSerializer
from notifications.utils import send_telegram_order_notification, send_telegram_cancellation_notification

# ==========================================
# 1. GET CART API
# ==========================================
class CartDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 2. UPDATE CART API (Add/Decrease/Remove)
# ==========================================
class CartUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        action = request.data.get('action') 
        quantity = int(request.data.get('quantity', 1))

        if not item_id or not action:
            return Response({"error": "item_id and action are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu_item = get_object_or_404(MenuItem, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=menu_item)
        
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


# ==========================================
# 3. MERGE CART API (LocalStorage Sync)
# ==========================================
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
            quantity = data.get('quantity', 1)
            menu_item = get_object_or_404(MenuItem, id=item_id)
            CartItem.objects.create(cart=cart, item=menu_item, quantity=quantity)

        serializer = CartSerializer(cart, context={'request': request})
        return Response({"status": True, "cart_data": serializer.data}, status=status.HTTP_200_OK)


# ==========================================
# 4. PLACE FINAL ORDER (With Telegram Alert)
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

        subtotal = 0
        for cart_item in cart.items.all():
            price = cart_item.item.offer_price if cart_item.item.offer_price else cart_item.item.actual_price
            subtotal += (price * cart_item.quantity)

        order = Order.objects.create(
            user=user, delivery_address=delivery_address, subtotal=subtotal,
            delivery_fee=0, total_amount=subtotal, payment_method=payment_method,
            payment_status='PENDING', order_status='PLACED'
        )

        for cart_item in cart.items.all():
            price = cart_item.item.offer_price if cart_item.item.offer_price else cart_item.item.actual_price
            OrderItem.objects.create(
                order=order, item=cart_item.item, item_name=cart_item.item.name,
                price=price, quantity=cart_item.quantity
            )
            # Update Inventory
            if cart_item.item.quantity >= cart_item.quantity:
                cart_item.item.quantity -= cart_item.quantity
            else:
                cart_item.item.quantity = 0 
            cart_item.item.save() 

        cart.items.all().delete()

        # Send Telegram Alert
        try:
            send_telegram_order_notification(order)
        except:
            pass

        return Response({"message": "Order placed successfully!", "order_id": order.id}, status=status.HTTP_201_CREATED)


# ==========================================
# 5. USER ORDER HISTORY
# ==========================================
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# ==========================================
# 6. CANCEL ORDER (Customer Side + Alert)
# ==========================================
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

        # Return items to stock
        for order_item in order.items.all():
            if order_item.item: 
                order_item.item.quantity += order_item.quantity
                order_item.item.save()

        # Send Telegram Alert
        try:
            send_telegram_cancellation_notification(order)
        except:
            pass

        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)


# ==========================================
# 7. ADMIN: LIST ORDERS (FIFO Listing)
# ==========================================
class AdminOrderListView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminOrStaff]
    
    def get_queryset(self):
        # FIFO: Oldest orders at top for kitchen
        queryset = Order.objects.all().order_by('created_at')
        status_param = self.request.query_params.get('status', None)
        
        if status_param:
            if status_param == 'HISTORY':
                queryset = queryset.filter(order_status__in=['DELIVERED', 'CANCELLED'])
            else:
                queryset = queryset.filter(order_status=status_param)
        return queryset


# ==========================================
# 8. ADMIN: UPDATE ORDER STATUS
# ==========================================
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
                    order_item.item.quantity += order_item.quantity
                    order_item.item.save()

        order.order_status = new_status
        order.save()
        return Response({"message": f"Order updated to {new_status}"}, status=status.HTTP_200_OK)
    

# ==========================================
# 9. ADMIN: GET ORDER STATS (Dashboard Counts)
# ==========================================
class AdminOrderStatsView(views.APIView):
    permission_classes = [IsAdminOrStaff] 

    def get(self, request):
        return Response({
            "new_orders": Order.objects.filter(order_status='PLACED').count(),
            "preparing": Order.objects.filter(order_status='PREPARING').count(),
            "on_the_way": Order.objects.filter(order_status='ON_THE_WAY').count(),
            "history": Order.objects.filter(order_status__in=['DELIVERED', 'CANCELLED']).count()
        }, status=status.HTTP_200_OK)