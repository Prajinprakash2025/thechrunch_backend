import firebase_admin
from firebase_admin import messaging
from .models import FCMDevice
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# ==========================================
# 1. FCM PUSH NOTIFICATION (Admin & Staff Only)
# ==========================================
def send_fcm_notification(exclude_user_id, title, body, data=None):
    """
    Sends Push Notifications to all Admin/Staff members, 
    excluding the user who triggered the action (order creator).
    """
    try:
        # Get all active FCM tokens for Admin and Staff, excluding the person who placed the order
        admin_staff_devices = FCMDevice.objects.filter(
            user__is_staff=True
        ).exclude(user=exclude_user_id)

        if not admin_staff_devices.exists():
            print("No admin or staff devices found to notify.")
            return None

        tokens = [device.fcm_token for device in admin_staff_devices]

        # Use Multicast to send to multiple tokens at once
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )

        response = messaging.send_multicast(message)
        print(f"Successfully sent FCM messages. Success count: {response.success_count}")
        return response

    except Exception as e:
        print(f"Error sending FCM notification: {e}")
    return None


# ==========================================
# 2. TELEGRAM NEW ORDER NOTIFICATION
# ==========================================
def send_telegram_order_notification(order):
    """Sends a Telegram message when a NEW ORDER is placed"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    
    if not bot_token or not chat_id:
        return 
        
    items_text = ""
    for item in order.items.all():
        items_text += f"▪️ {item.quantity}x {item.item_name}\n"
        
    message = (
        f"🚨 *NEW ORDER RECEIVED!* 🚨\n\n"
        f"🏷 *Order ID:* #{order.id}\n"
        f"👤 *Customer:* {order.user.first_name} {order.user.last_name}\n"
        f"📞 *Phone:* {order.user.phone_number}\n"
        f"💰 *Total Amount:* ₹{order.total_amount}\n\n"
        f"🍽 *Items Ordered:*\n{items_text}\n"
        f"🚚 *Payment:* {order.payment_method} ({order.payment_status})"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram error: {e}")


# ==========================================
# 3. TELEGRAM CANCELLATION NOTIFICATION
# ==========================================
def send_telegram_cancellation_notification(order):
    """Sends a Telegram message when an order is CANCELLED"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    
    if not bot_token or not chat_id:
        return 

    customer_name = f"{order.user.first_name} {order.user.last_name}"
    
    message = (
        f"⚠️ *ORDER CANCELLED* ⚠️\n\n"
        f"🏷 *Order ID:* #{order.id}\n"
        f"👤 *Customer:* {customer_name}\n"
        f"❌ *Status:* The order has been cancelled by the customer."
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram error: {e}")