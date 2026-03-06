from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

# Make sure these model imports match your exact app structure!
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem 
from accounts.models import Address
from .serializers import CartSerializer, OrderSerializer

# ==========================================
# 1. GET CART API (To load the cart page)
# ==========================================
class CartDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # 🌟 FIX: Added context so Django builds the full https:// domain for images!
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
        action = request.data.get('action') # 'add', 'decrease', or 'remove'

        if not item_id or not action:
            return Response({"error": "item_id and action are required"}, status=status.HTTP_400_BAD_REQUEST)

        menu_item = get_object_or_404(MenuItem, id=item_id)
        
        # Get or create the item in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=menu_item)
        if created:
            cart_item.quantity = 0 # Start at 0 so 'add' makes it 1

        # Perform the action
        if action == 'add':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        # 🌟 FIX: Added context so React gets the full image URLs after an update!
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

        # Clear old backend cart to match local storage
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

        # 🌟 FIX: Added context so React gets the full image URLs after logging in!
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

        delivery_fee = 0 # Can be made dynamic later
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
            
            # 1. Create the permanent receipt (OrderItem)
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                item_name=cart_item.item.name,
                price=price,
                quantity=cart_item.quantity
            )

            # 🌟 NEW FIX: Reduce the actual stock of the food item in the inventory!
            if cart_item.item.quantity >= cart_item.quantity:
                cart_item.item.quantity -= cart_item.quantity
            else:
                cart_item.item.quantity = 0 # Prevent negative stock just in case
            
            cart_item.item.save() # Save the new stock level to the database!

        # Clear cart after placing order
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
        # Return orders belonging to the logged-in user, newest first
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


# ==========================================
# 6. CANCEL ORDER API 
# ==========================================
class CancelOrderView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        # Fetch the order belonging to the logged-in user
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # 1. Check if the order can be cancelled
        if order.order_status != 'PLACED':
            return Response(
                {"error":  "Sorry, this order can no longer be cancelled."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Update order status to CANCELLED
        order.order_status = 'CANCELLED'
        order.save()

        # 3. Return the items back to the inventory stock
        for order_item in order.items.all():
            if order_item.item: # Check if the MenuItem still exists in the database
                order_item.item.quantity += order_item.quantity
                order_item.item.save()

        return Response(
            {"message": "Order cancelled successfully"}, 
            status=status.HTTP_200_OK
        )