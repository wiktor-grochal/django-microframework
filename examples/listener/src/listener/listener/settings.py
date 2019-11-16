import os


# ######################################### #
# ################ DJANGO ################# #
# ######################################### #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '_6t$4(&9h@^1+qi)98l7v33rtg=1wf%dpl7@0$#(f2(3kc@1*h'

if os.environ.get('DEBUG', '0') == '1':
    DEBUG = True
    DJANGO_LOG_LEVEL = 'DEBUG'
else:
    DEBUG = False
    DJANGO_LOG_LEVEL = 'INFO'

ALLOWED_HOSTS = [host for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')]

SITE_ID = 1

ADMIN_SITE_HEADER = os.environ.get('APP_VERSION', 'listener')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'mptt',
    'debug_toolbar',
    'example',
    'microframework',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'listener.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'listener.wsgi.application'

DATABASES = {
    'default': {
        'init_command': os.environ.get('DJANGO_DATABASE_INIT_COMMAND', ''),
        'ENGINE': os.environ.get('DJANGO_DATABASE_ENGINE', ''),
        'NAME': os.environ.get('DJANGO_DATABASE_NAME', ''),
        'PASSWORD': os.environ.get('DJANGO_DATABASE_PASSWORD', ''),
        'USER': os.environ.get('DJANGO_DATABASE_USER', ''),
        'HOST': os.environ.get('DJANGO_DATABASE_HOST', ''),
        'PORT': os.environ.get('DJANGO_DATABASE_PORT', '')
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] [{asctime}] [{module}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'example': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
        },
        'listener': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
        },
    }
}


# ################################################ #
# ############### DEBUG TOOLBAR ################## #
# ################################################ #

if DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
    }

MICROFRAMEWORK_SERVICE_CLASS = "example.service:ListenerService"
