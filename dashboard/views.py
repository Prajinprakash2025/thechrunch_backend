from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from accounts.permissions import IsAdminOrStaff
from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminDashboardView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # Using localdate() to ensure we get the correct date in IST
        today = timezone.localdate()

        # 1. TOP STATS
        total_orders = Order.objects.count()
        pending_dispatch = Order.objects.filter(order_status__in=['PLACED', 'PREPARING']).count()
        active_customers = User.objects.filter(role='user', is_blocked=False).count()
        total_revenue = Order.objects.filter(order_status='DELIVERED').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # 2. WEEKLY ORDER VOLUME (Monday to Sunday)
        weekly_volume = []
        # Calculate start of the week based on localdate
        start_of_week = today - timedelta(days=today.weekday())
        
        for i in range(7):
            current_day = start_of_week + timedelta(days=i)
            # Filtering by exact date instead of datetime ranges for accuracy with localdate
            day_orders = Order.objects.filter(created_at__date=current_day).count()
            weekly_volume.append({
                "day": current_day.strftime("%a"),
                "orders": day_orders
            })

        # 3. LEADERBOARD
        top_items = OrderItem.objects.values('item_name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        leaderboard = [{"item": item['item_name'], "sold": item['total_sold']} for item in top_items]

        # 4. ATTENTION NEEDED
        lowest_items = OrderItem.objects.values('item_name').annotate(
            total_sold=Sum('quantity')
        ).order_by('total_sold')[:6]
        
        attention_needed = [{"item": item['item_name'], "issue": "Low Demand"} for item in lowest_items]

        # 5. ACTIVE DISPATCH
        active_orders = Order.objects.filter(order_status='ON_THE_WAY').order_by('-created_at')[:5]
        active_dispatch = [
            {
                "id": f"#{order.id}", 
                "status": order.get_order_status_display().upper(), 
                "time": "Recent" 
            } for order in active_orders
        ]

        return Response({
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
        })