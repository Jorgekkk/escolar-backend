import os
import dj_database_url  # <--- IMPORTANTE: Necesario para Render

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CLAVE SECRETA
# En producción real deberías usar variables de entorno, pero por ahora esto funciona.
SECRET_KEY = os.environ.get('SECRET_KEY', '-_&+lsebec(whhw!%n@ww&1j=4-^j_if9x8$q778+99oz&!ms2')

# DEBUG
# Si estamos en Render, DEBUG será False. Si estamos en local, será True.
# (Render define automáticamente la variable 'RENDER').
DEBUG = 'RENDER' not in os.environ

# ALLOWED HOSTS
# El asterisco '*' permite que tu backend responda a la URL que te asigne Render automáticamente.
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',             # necesarios para los filtros de DRF
    'rest_framework',
    'rest_framework.authtoken',   # conserva soporte de tokens de DRF
    'corsheaders',                # librería CORS
    'app_escolar_api',            # Tu aplicación principal
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    # <--- IMPORTANTE: Whitenoise para archivos estáticos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',         # CORS debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CONFIGURACIÓN CORS (Conexión con Angular)
# Esto permite que Vercel y tu Localhost se comuniquen con Django.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    # Agrega aquí tu URL de Vercel cuando la tengas, ejemplo:
    # "https://mi-escuela-app.vercel.app",
]

# Si tienes problemas de conexión al inicio, puedes descomentar la siguiente línea
# para permitir todo temporalmente:
CORS_ALLOW_ALL_ORIGINS = True 

CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:4200",
    # "https://mi-escuela-app.vercel.app", 
]

ROOT_URLCONF = 'app_escolar_api.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'app_escolar_api.wsgi.application'

# ---------------------------------------------------------
# BASE DE DATOS (HÍBRIDA: MySQL Local / PostgreSQL Render)
# ---------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, "my.cnf"),
            'charset': 'utf8mb4',
        }
    }
}

# Configuración automática para Render
db_from_env = dj_database_url.config(conn_max_age=600)

if db_from_env:
    # Si detectamos Render, reemplazamos COMPLETAMENTE la configuración
    # para usar PostgreSQL y evitar el error de 'read_default_file'
    DATABASES['default'] = db_from_env


# VALIDADORES DE CONTRASEÑA
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------
# ARCHIVOS ESTÁTICOS (STATIC FILES)
# ---------------------------------------------------------
STATIC_URL = '/static/'

# Esto le dice a Django dónde poner los archivos cuando ejecutes 'collectstatic' en Render
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Motor de almacenamiento para Whitenoise (comprime y sirve los archivos en producción)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# REST FRAMEWORK CONFIG
REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        # Asegúrate de que esta ruta sea correcta en tu proyecto:
        'app_escolar_api.models.BearerTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}