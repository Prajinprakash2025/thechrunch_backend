from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        
        if header is None:
            # Header illengil cookie-il ninnu edukkan nokkunnu
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            # Token validate cheyyunnu
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            # 🌟 Token expired aayalo invalid aayalo error kanikkathe 
            # None thirichu vidum. Appol system login cheyyan anuvadhikkum.
            return None