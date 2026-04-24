from pathlib import Path
import environ
import os

env = environ.Env(DEBUG=(bool, True))

# BASE_DIR se usa como referencia central para encontrar .env, base de datos y archivos estáticos.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'movies.apps.MoviesConfig',
    'users.apps.UsersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'mymovies.urls'

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

WSGI_APPLICATION = 'mymovies.wsgi.application'

# En desarrollo se usa SQLite porque simplifica levantar el proyecto sin servicios extra.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Django buscará assets estáticos aquí durante desarrollo.
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Las credenciales de TMDB viven en .env para no hardcodearlas en el repositorio.
TMDB_API_KEY = env('TMDB_API_KEY', default='')
TMDB_API_TOKEN = env('TMDB_API_TOKEN', default='')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/w500'

# Estas rutas centralizan a dónde se manda al usuario cuando inicia o cierra sesión.
LOGIN_URL = '/users/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
