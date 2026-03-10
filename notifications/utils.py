import requests
from django.conf import settings

def send_telegram_order_notification(order):
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    
    if not bot_token or not chat_id:
        return # If token is not set, do nothing
        
    # Formatting the food items list
    items_text = ""
    for item in order.items.all():
        items_text += f"▪️ {item.quantity}x {item.item_name}\n"
        
    # The message that will be sent to the Telegram Group
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
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        # Send the message to Telegram
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")