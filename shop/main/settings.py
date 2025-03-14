
from pathlib import Path
import os
import smtplib


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent




# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g_rw2ohio!k=3yd_km_*utw!52=o9x7$i7=3lww%%%dn$e9g0u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.header_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# # settings.py
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'INFO',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['console'],
#             'level': 'INFO',
#             'propagate': True,
#         },
#     },
# }

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# PAYMENT_METHODS = [
#     ('stripe', 'Stripe'),
#     ('paypal', 'PayPal'),
#     ('other', 'Autre'),
# ]


# Stripe configuration
STRIPE_SECRET_KEY = "sk_test_51PjpfOEpPZtVw7C2NGfXsCU0MVENXOcDeFy7IuifL5dGipfia6qEpzZCCEXqci0CWKlzmVQeVVIPzSnrJ2RfHrLQ00R7eS1u2c"  # Remplace par ta clé secrète réelle
STRIPE_PUBLISHABLE_KEY = "pk_test_51PjpfOEpPZtVw7C2UroUPSAVYzMfys3J001LPhUbfgWVLtVHzEExScSMNKdWTloCRgukcqfh0rbXUO5pKZPcWDoh00vFZqfOwK"  # Remplace par ta clé publique réelle
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Stockage en base de données
SESSION_COOKIE_AGE = 1209600  # Durée de vie de la session (2 semaines par défaut)
SESSION_COOKIE_SECURE = False  # Mets à True en production avec HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True  # Sauvegarde la session à chaque requête
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Ne pas expirer à la fermeture du navigateur

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
MEDIA_ROOT =os.path.join(BASE_DIR,'media')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

LOGIN_REDIRECT_URL = '/test/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_CURRENCY = 'eur'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'arman.margaryan.fr@gmail.com'
EMAIL_HOST_PASSWORD = 'gfru bqov zuns gdgz'
DEFAULT_FROM_EMAIL = 'arman.margaryan.fr@gmail.com'

