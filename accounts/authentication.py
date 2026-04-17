class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        
        if header is None:
            # Header ഇല്ലെങ്കിൽ കുക്കിയിൽ നിന്ന് എടുക്കാൻ നോക്കുന്നു
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            # ടോക്കൺ വാലിഡേറ്റ് ചെയ്യുന്നു
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except:
            # 🌟 ഇതാണ് മെയിൻ മാറ്റം:
            # ടോക്കൺ എക്സ്പെയർ ആയാലോ ഇൻവാലിഡ് ആയാലോ എറർ കാണിക്കാതെ 
            # വെറുതെ None തിരിച്ചു വിടുക. അപ്പോൾ സിസ്റ്റം ലോഗിൻ ചെയ്യാൻ അനുവദിക്കും.
            return None