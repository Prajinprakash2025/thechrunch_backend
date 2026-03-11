from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminOrStaff
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

class RevenueDashboardView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        # 1. Total Sales Income (All-Time DELIVERED)
        total_revenue_data = Order.objects.filter(
            order_status='DELIVERED'
        ).aggregate(total=Sum('total_amount'))
        total_revenue = total_revenue_data['total'] or 0.0

        # 2. Today's Income & Growth
        # Calculate Today's Sales
        today_sales_data = Order.objects.filter(
            order_status='DELIVERED',
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))
        today_sales = today_sales_data['total'] or 0.0

        # Calculate Yesterday's Sales
        yesterday_sales_data = Order.objects.filter(
            order_status='DELIVERED',
            created_at__date=yesterday
        ).aggregate(total=Sum('total_amount'))
        yesterday_sales = yesterday_sales_data['total'] or 0.0

        # Growth Logic (Handling division by zero)
        growth_percentage = 0.0
        if yesterday_sales > 0:
            growth_percentage = ((today_sales - yesterday_sales) / yesterday_sales) * 100
        elif yesterday_sales == 0 and today_sales > 0:
            growth_percentage = 100.0 # From 0 to something means 100% growth
        else:
            growth_percentage = 0.0 # Both days 0, or zero as requested

        # 3. Sales Performance Chart (Last 7 Days)
        seven_days_ago = today - timedelta(days=6) # 6 days + today = 7 days
        graph_data = []
        
        # Loop through each of the last 7 days to get sales per day
        for i in range(7):
            current_date = seven_days_ago + timedelta(days=i)
            daily_sales_data = Order.objects.filter(
                order_status='DELIVERED',
                created_at__date=current_date
            ).aggregate(total=Sum('total_amount'))
            
            daily_sales = daily_sales_data['total'] or 0.0
            
            graph_data.append({
                "date": current_date.strftime("%b %d"), # Format like 'Feb 11'
                "revenue": daily_sales
            })

        # Final Response combining all 3 points
        response_data = {
            "total_sales_income": total_revenue,
            "todays_income": {
                "amount": today_sales,
                "growth_percentage": round(growth_percentage, 2)
            },
            "sales_performance": graph_data
        }

        return Response(response_data)