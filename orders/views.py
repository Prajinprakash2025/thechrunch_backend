from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Cart, CartItem, Order, OrderItem
from inventory.models import MenuItem
from accounts.models import Address
from .serializers import CartSerializer, OrderSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
# Make sure to import your MenuItem model here!
# from store.models import MenuItem 

# ============================================================
# BULK MERGE CART API (Sync LocalStorage to Database)
# ============================================================
class CartMergeView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        # 1. Get or create the Cart for this logged-in user
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # 2. Grab the array of items from the React frontend
        items_data = request.data.get('items', [])

        if not items_data:
            return Response({"message": "No items to merge"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Clear the old backend cart completely to avoid duplicate junk
        # Because we trust the frontend localStorage as the "source of truth" right now!
        cart.items.all().delete()

        # 4. Loop through the array and save the fresh list to the database
        for data in items_data:
            item_id = data.get('item_id')
            quantity = data.get('quantity', 1)

            # Link it to the actual menu item
            menu_item = get_object_or_404(MenuItem, id=item_id)

            # Create the fresh cart item
            CartItem.objects.create(
                cart=cart,
                item=menu_item,
                quantity=quantity
            )

        return Response({
            "status": True, 
            "message": "Local cart successfully merged to database!"
        }, status=status.HTTP_200_OK)
# ==========================================
# 3. PLACE FINAL ORDER
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

        subtotal = sum(item.total_price for item in cart.items.all())
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
            
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                item_name=cart_item.item.name,
                price=price,
                quantity=cart_item.quantity
            )

        # Clear cart after placing order
        cart.items.all().delete()

        return Response({
            "message": "Order placed successfully!",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)

# ==========================================
# 4. ORDER HISTORY (List all past orders)
# ==========================================
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return orders belonging to the logged-in user, newest first
        return Order.objects.filter(user=self.request.user).order_by('-created_at')