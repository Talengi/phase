"""Production settings and globals.

We will no rely on environments variable for configuration,
because it works poorly with mod_wsgi.

See:
    * https://code.google.com/p/modwsgi/wiki/ApplicationIssues#Application_Environment_Variables
    * https://github.com/twoscoops/django-twoscoops-project/issues/60#issuecomment-25935406

Instead, we are using a private configuration file that MUST not be
added to the git repository to protect private configuration data.
"""

from .base import *  # noqa
from .base import INSTALLED_APPS, SITE_NAME  # Avoid pyflakes complains

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

try:
    import prod_private
except ImportError:
    raise ImproperlyConfigured("Create a prod_private.py file in settings")


def get_prod_setting(setting, optional_import=False):
    """Get the setting or return exception """
    try:
        return getattr(prod_private, setting)
    except AttributeError:
        error_msg = "The %s setting is missing from prod settings" % setting
        if not optional_import:
            raise ImproperlyConfigured(error_msg)
        return None


# Template configuration: enable compiled templates caching
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'loaders': [
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'accounts.context_processors.navigation',
                'accounts.context_processors.branding_on_login',
                'notifications.context_processors.notifications',
                'reviews.context_processors.reviews',
                'dashboards.context_processors.dashboards',
            ],
        },
    },
]

INSTALLED_APPS += (
    'gunicorn',
    'raven.contrib.django.raven_compat',
)

# ######### EMAIL CONFIGURATION
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME
DEFAULT_FROM_EMAIL = get_prod_setting('DEFAULT_FROM_EMAIL')
EMAIL_BACKEND = get_prod_setting('EMAIL_BACKEND')
EMAIL_HOST = get_prod_setting('EMAIL_HOST')
EMAIL_HOST_PASSWORD = get_prod_setting('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = get_prod_setting('EMAIL_HOST_USER')
EMAIL_PORT = get_prod_setting('EMAIL_PORT')
EMAIL_USE_TLS = get_prod_setting('EMAIL_USE_TLS')
SERVER_EMAIL = get_prod_setting('SERVER_EMAIL')
SEND_EMAIL_REMINDERS = get_prod_setting('SEND_EMAIL_REMINDERS')
SEND_NEW_ACCOUNTS_EMAILS = get_prod_setting('SEND_NEW_ACCOUNTS_EMAILS')

# ######### DATABASE CONFIGURATION
DATABASES = get_prod_setting('DATABASES')

# ######### CACHE CONFIGURATION
CACHES = get_prod_setting('CACHES')

# ######### SECRET CONFIGURATION
SECRET_KEY = get_prod_setting('SECRET_KEY')

# ######### CUSTOM CONFIGURATION
ALLOWED_HOSTS = get_prod_setting('ALLOWED_HOSTS')
USE_X_SENDFILE = True

# ######### TRANSMITTALS IMPORT CONFIGURATION
TRS_IMPORTS_CONFIG = get_prod_setting('TRS_IMPORTS_CONFIG')

# ######### LOGS CONFIG
USE_SENTRY = get_prod_setting('USE_SENTRY')
RAVEN_CONFIG = get_prod_setting('RAVEN_CONFIG')

# ######### CUSTOM PDFS AND BRANDING
COMPANY_LOGOS = get_prod_setting('COMPANY_LOGOS', optional_import=True)
PDF_CONFIGURATION = get_prod_setting(
    'PDF_CONFIGURATION', optional_import=True)

# ######### LOGIN BRANDING
DISPLAY_LOGIN_BRANDING = get_prod_setting(
    'DISPLAY_LOGIN_BRANDING', optional_import=True)

# ######### SECURITY
try:
    USE_SSL = get_prod_setting('USE_SSL')
except ImproperlyConfigured:
    USE_SSL = False

if USE_SSL:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # You *will* open critical security holes if you set this
    # without knowing what you are doing. Read dj doc carefully.
    # https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
    SECURE_PROXY_SSL_HEADER = get_prod_setting(
        'SECURE_PROXY_SSL_HEADER', optional_import=True)
