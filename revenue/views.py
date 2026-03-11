from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import IsAdminOrStaff
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from notifications.models import AdminNotification
from rest_framework import status

class RevenueDashboardView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # Using localdate() to get the exact current date in IST (Indian Standard Time)
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        
        # 1. Total Sales Income 
        total_revenue_data = Order.objects.filter(
            order_status='DELIVERED'
        ).aggregate(total=Sum('total_amount'))
        total_revenue = total_revenue_data['total'] or 0

        # 2. Today's Income & Growth
        today_sales_data = Order.objects.filter(
            order_status='DELIVERED',
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))
        today_sales = today_sales_data['total'] or 0

        yesterday_sales_data = Order.objects.filter(
            order_status='DELIVERED',
            created_at__date=yesterday
        ).aggregate(total=Sum('total_amount'))
        yesterday_sales = yesterday_sales_data['total'] or 0

        # Growth Logic
        growth_percentage = 0
        if yesterday_sales > 0:
            growth_percentage = ((today_sales - yesterday_sales) / yesterday_sales) * 100
        elif yesterday_sales == 0 and today_sales > 0:
            growth_percentage = 100

        # 3. Sales Performance Chart (Last 7 Days)
        seven_days_ago = today - timedelta(days=6)
        graph_data = []
        
        for i in range(7):
            current_date = seven_days_ago + timedelta(days=i)
            daily_sales_data = Order.objects.filter(
                order_status='DELIVERED',
                created_at__date=current_date
            ).aggregate(total=Sum('total_amount'))
            
            daily_sales = daily_sales_data['total'] or 0
            
            graph_data.append({
                "date": current_date.strftime("%b %d"),
                "revenue": daily_sales
            })

        response_data = {
            "total_sales_income": total_revenue,
            "todays_income": {
                "amount": today_sales,
                "growth_percentage": round(float(growth_percentage), 2) # float() added to be safe
            },
            "sales_performance": graph_data
        }

        return Response(response_data)