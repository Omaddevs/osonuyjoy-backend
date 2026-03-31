import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-unsafe-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# Xavfsizlik uchun localhost va production domenlarini qo'shdik
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,testserver,osonuyjoy-backend.onrender.com"
    ).split(",")
    if h.strip()
]
# Render har deployda yangi subdomain berishi mumkin; avtomatik qo'shamiz.
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles", # Static fayllar uchun muhim
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "listings",
    "reels",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # CSS chiqishi uchun SHU QATORNI QO'SHDIK
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# --- Static va Media sozlamalari ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise uchun qo'shimcha siqish (ixtiyoriy lekin foydali)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- REST Framework sozlamalari ---
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer", # Debug paytida API ko'rinishi uchun
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
    # `ScopedRateThrottle` uchun kerak (masalan: `review_create` va `review_helpful`)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Foydalanuvchi 1 daqiqada maksimal necha marta sharh qo'shishi mumkin
        "review_create": "5/min",
        # "Foydali" ovozini spamdan himoya
        "review_helpful": "20/min",
        # E'lon arizasi (to'lov chek bilan)
        "submission_create": "10/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Oson uy-joy API",
    "DESCRIPTION": "Ko'chmas mulk va reels API.",
    "VERSION": "1.0.0",
}

# --- CORS va CSRF sozlamalari ---

# Render'dagi backend manzilingizni ishonchli ro'yxatga qo'shish shart (Admin login uchun)
CSRF_TRUSTED_ORIGINS = [
    "https://osonuyjoy-backend.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if render_host:
    rh = f"https://{render_host}"
    if rh not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(rh)

# Frontend'dan so'rovlar kelishi uchun
_cors = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://osonuyjoy-backend.onrender.com")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors.split(",") if o.strip()]

# Agar sizda Frontend alohida domenda bo'lsa (masalan Vercel'da), uni ham qo'shing
# Masalan: https://osonuyjoy.vercel.app

CORS_ALLOW_CREDENTIALS = True