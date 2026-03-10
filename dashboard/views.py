from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

# Import custom permissions
from accounts.permissions import IsAdminOrStaff

# Import your actual models here. Adjust the names if they are different.
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminDashboardView(APIView):
    # Only logged-in admins or staff can see this dashboard
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        today = timezone.now()

        # ==========================================
        # 1. TOP STATS
        # ==========================================
        total_orders = Order.objects.count()
        
        # Using 'PLACED' and 'PREPARING' matching your ORDER_STATUS choices
        pending_dispatch = Order.objects.filter(status__in=['PLACED', 'PREPARING']).count()
        
        # Excludes blocked users from the active customers count
        active_customers = User.objects.filter(role='user', is_blocked=False).count()
        
        # Using 'DELIVERED' to calculate total revenue
        total_revenue = Order.objects.filter(status='DELIVERED').aggregate(Sum('total_price'))['total_price__sum'] or 0

        # ==========================================
        # 2. WEEKLY ORDER VOLUME (Monday to Sunday)
        # ==========================================
        weekly_volume = []
        
        # Find the Monday of the current week (weekday() returns 0 for Monday, 6 for Sunday)
        start_of_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Loop 7 days from Monday to Sunday
        for i in range(7):
            day_start = start_of_week + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Count orders created on this specific day
            day_orders = Order.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
            day_name = day_start.strftime("%a")
            
            weekly_volume.append({
                "day": day_name,
                "orders": day_orders
            })

        # ==========================================
        # 3. LEADERBOARD (Top 5 selling items)
        # ==========================================
        top_items = OrderItem.objects.values('menu_item__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        leaderboard = [
            {"item": item['menu_item__name'], "sold": item['total_sold']} 
            for item in top_items
        ]

        # ==========================================
        # 4. ATTENTION NEEDED (Lowest 4 selling items)
        # ==========================================
        # Sorting by total_sold ascending to get the lowest demand items
        lowest_items = OrderItem.objects.values('menu_item__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('total_sold')[:4]

        attention_needed = [
            {
                "item": item['menu_item__name'], 
                "issue": "Low Demand"
            }
            for item in lowest_items
        ]

        # ==========================================
        # 5. ACTIVE DISPATCH (Recent active orders)
        # ==========================================
        # Using 'ON_THE_WAY' matching your ORDER_STATUS choices
        active_orders = Order.objects.filter(status='ON_THE_WAY').order_by('-created_at')[:5]
        active_dispatch = [
            {
                "id": f"#{order.id}", 
                "status": order.get_status_display().upper(), 
                "time": "Recent" 
            } 
            for order in active_orders
        ]

        # Combine everything into one JSON response
        dashboard_data = {
            "stats": {
                "total_orders": total_orders,
                "pending_dispatch": pending_dispatch,
                "active_customers": active_customers,
                "total_revenue": total_revenue
            },
            "weekly_volume": weekly_volume,
            "leaderboard": leaderboard,
            "attention_needed": attention_needed,
            "active_dispatch": active_dispatch
        }

        return Response(dashboard_data)