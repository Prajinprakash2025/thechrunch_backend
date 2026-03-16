import requests
import json
from django.conf import settings

def send_whatsapp_otp(phone_number, otp):
    """
    Meta Graph API ഉപയോഗിച്ച് WhatsApp OTP അയക്കുന്നു.
    തൽക്കാലം hello_world ടെംപ്ലേറ്റ് ഉപയോഗിക്കുന്നു.
    """
    # 1. നിങ്ങളുടെ Phone Number ID സ്ക്രീൻഷോട്ടിൽ ഉള്ളത്: 1050026328191395
    url = f"https://graph.facebook.com/v22.0/1050026328191395/messages"
    
    # 2. നിങ്ങളുടെ Permanent Token ഇവിടെ കൃത്യമായി നൽകുക
    # ശ്രദ്ധിക്കുക: ലിങ്ക് അല്ല, EAAS... എന്ന് തുടങ്ങുന്ന ആ നീളമുള്ള കോഡ് വേണം നൽകാൻ.
    token = "EAASxU3ADxXMBQwH9TJD0lTGsZB9RkPMWztqJBKKT7DwDylpFTJS35hZCMPyrom7CjP8i3ycuRZB01JgLJlcIrZBdNLRsoiPaxGffjRJemsii9eCdAe1MrO3SbUUiTOkYvZCW69YiUwpcpPDWyl4Ge22MZBapQ2CaZAbE2GK6A2bctC4KHZAEjI6RBUiI9cnxbEmzLQZDZD"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    # ഇന്ത്യയിലെ നമ്പറാണെങ്കിൽ 91 ചേർക്കുന്നു
    if not phone_number.startswith('91'):
        phone_number = f"91{phone_number}"
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        result = response.json()
        print("WhatsApp API Status:", response.status_code)
        print("WhatsApp API Response:", result)
        return result
    except Exception as e:
        print("WhatsApp Error:", str(e))
        return None