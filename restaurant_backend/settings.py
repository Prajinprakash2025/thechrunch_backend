from pathlib import Path
import os
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials

# 1. Define BASE_DIR first
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Tell dotenv EXACTLY where to find the .env file
env_path = BASE_DIR / '.env'
load_dotenv(env_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party libraries
    'rest_framework',
    'rest_framework_simplejwt',  # JWT support
    'corsheaders',               # For React frontend
    'rest_framework_simplejwt.token_blacklist',  
    
    # Your apps
    'contact',
    "accounts",
    "bookings",
    "inventory",
    'banners',
    'site_settings',
    'orders',
    'customers',
    'notifications',
    'dashboard',
    'revenue',
    'feedback',
    'faq',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restaurant_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restaurant_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   
}


AUTH_USER_MODEL = "accounts.User"
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True



# settings.py
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000", # Or whatever port your friend is using
# ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173 ",
    "https://foo-d-elivery.netlify.app",
    "http://thecrunchindia.com",

]

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')       
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')  

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# FIREBASE FCM SETUP
# ==========================================
# Ensure the firebase-key.json file is in your BASE_DIR (same folder as manage.py)
# If your filename is firebase-key.json.json, change it below.
FIREBASE_KEY_PATH = os.path.join(BASE_DIR, 'firebase-key.json.json')

# Initialize Firebase only if it hasn't been initialized already
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("🔥 Firebase initialized successfully!")
    except Exception as e:
        print(f"⚠️ Error initializing Firebase: {e}")



REST_FRAMEWORK = {
    # This tells Django to actively look for Bearer JWT Tokens!
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    # 🚀 THE FIX: Add this new section for Global Permissions
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny', # Default permission
        'accounts.permissions.IsNotBlocked',   # Our new block check permission
    ),

    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'otp_requests': '3/m',
    }
}