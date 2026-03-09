from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from accounts.permissions import IsAdminOrStaff
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem 
from accounts.models import Address
from .serializers import CartSerializer, OrderSerializer, AdminOrderSerializer

# ==========================================
# 1. GET CART API (To load the cart page)
# ==========================================
class CartDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 2. UPDATE CART API (Single Item +, -, or Delete)
# ==========================================
class CartUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        item_id = request.data.get('item_id')
        action = request.data.get('action') 
        
        # 🚀 THE FIX: Get the quantity from frontend request (Default is 1 if not provided)
        quantity = int(request.data.get('quantity', 1))

        if not item_id or not action:
            return Response({"error": "item_id and action are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu_item = get_object_or_404(MenuItem, id=item_id)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=menu_item)
        if created:
            cart_item.quantity = 0 

        if action == 'add':
            # 🚀 THE FIX: Add the exact quantity requested by frontend
            cart_item.quantity += quantity
            cart_item.save()
        elif action == 'decrease':
            # 🚀 THE FIX: Decrease by the exact quantity requested
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
        return Response({
            "message": f"Successfully performed {action}",
            "cart_data": serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================
# 3. MERGE CART API (Bulk Sync from LocalStorage on Login)
# ============================================================
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

            CartItem.objects.create(
                cart=cart,
                item=menu_item,
                quantity=quantity
            )

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "status": True, 
            "message": "Local cart successfully merged to database!",
            "cart_data": serializer.data
        }, status=status.HTTP_200_OK)


# ==========================================
# 4. PLACE FINAL ORDER
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

        if not address_id:
            return Response({"error": "Delivery address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = 0
        for cart_item in cart.items.all():
            price = cart_item.item.offer_price if cart_item.item.offer_price else cart_item.item.actual_price
            subtotal += (price * cart_item.quantity)

        delivery_fee = 0 
        total_amount = subtotal + delivery_fee

        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='PENDING',
            order_status='PLACED'
        )

        for cart_item in cart.items.all():
            price = cart_item.item.offer_price if cart_item.item.offer_price else cart_item.item.actual_price
            
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                item_name=cart_item.item.name,
                price=price,
                quantity=cart_item.quantity
            )

            if cart_item.item.quantity >= cart_item.quantity:
                cart_item.item.quantity -= cart_item.quantity
            else:
                cart_item.item.quantity = 0 
            
            cart_item.item.save() 

        cart.items.all().delete()

        return Response({
            "message": "Order placed successfully!",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)

# ==========================================
# 5. ORDER HISTORY (List all past orders)
# ==========================================
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# ==========================================
# 6. CANCEL ORDER API 
# ==========================================
# ==========================================
# 6. CANCEL ORDER API (Customer Side)
# ==========================================
class CancelOrderView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Condition: Customer can ONLY cancel if it is strictly 'PLACED'
        if order.order_status != 'PLACED':
            return Response(
                {"error":  "Sorry, this order is already being processed and can no longer be cancelled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark as Cancelled and record WHO cancelled it (The Customer)
        order.order_status = 'CANCELLED'
        order.cancelled_by = request.user
        order.save()

        # Return the items back to the inventory stock
        for order_item in order.items.all():
            if order_item.item: 
                order_item.item.quantity += order_item.quantity
                order_item.item.save()

        return Response(
            {"message": "Order cancelled successfully"}, 
            status=status.HTTP_200_OK
        )

# ==========================================
# 7. ADMIN: LIST ORDERS API (Dashboard Filters)
# ==========================================
class AdminOrderListView(generics.ListAPIView):
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminOrStaff]
    def get_queryset(self):
        queryset = Order.objects.all().order_by('created_at')
        
        order_status = self.request.query_params.get('status', None)
        
        if order_status:
            if order_status == 'HISTORY':
                queryset = queryset.filter(order_status__in=['DELIVERED', 'CANCELLED'])
            else:
                queryset = queryset.filter(order_status=order_status)
                
        return queryset

# ==========================================
# 8. ADMIN: UPDATE ORDER STATUS API
# ==========================================
class AdminOrderStatusUpdateView(views.APIView):
    permission_classes = [IsAdminOrStaff]   
    @transaction.atomic
    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        
        valid_statuses = ['PLACED', 'PREPARING', 'ON_THE_WAY', 'DELIVERED', 'CANCELLED']
        
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the Admin/Staff cancels the order, record it and return stock
        if new_status == 'CANCELLED' and order.order_status != 'CANCELLED':
            order.cancelled_by = request.user
            # Return stock logic for admin cancellation
            for order_item in order.items.all():
                if order_item.item: 
                    order_item.item.quantity += order_item.quantity
                    order_item.item.save()

        order.order_status = new_status
        order.save()
        
        return Response(
            {"message": f"Order #{order.id} status updated to {new_status}."}, 
            status=status.HTTP_200_OK
        )
    

# ==========================================
# 9. ADMIN: GET ORDER STATS (For Tab Counts)
# ==========================================
class AdminOrderStatsView(views.APIView):
    # Use IsAdminOrStaff if you updated your permissions, otherwise IsAdminUser
    permission_classes = [IsAdminOrStaff] 

    def get(self, request):
        # Count orders based on their current status
        placed_count = Order.objects.filter(order_status='PLACED').count()
        preparing_count = Order.objects.filter(order_status='PREPARING').count()
        on_the_way_count = Order.objects.filter(order_status='ON_THE_WAY').count()
        
        # History includes both delivered and cancelled orders
        history_count = Order.objects.filter(order_status__in=['DELIVERED', 'CANCELLED']).count()

        return Response({
            "new_orders": placed_count,
            "preparing": preparing_count,
            "on_the_way": on_the_way_count,
            "history": history_count
        }, status=status.HTTP_200_OK)