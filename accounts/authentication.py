from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom Authentication Class.
    Tells Django REST Framework to look for the JWT token inside the HTTP-Only cookie.
    """
    def authenticate(self, request):
        # Aadyam standard Header-il token undo ennu nokkum
        header = self.get_header(request)
        
        # Header-il illengil (Cookie aayathukondu undavilla), Cookie-il ninnu edukkum
        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        # Token Validate cheythu User-e return cheyyunnu
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token