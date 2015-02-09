"""Production settings and globals.

We will no rely on environments variable for configuration,
because it works poorly with mod_wsgi.

See:
    * https://code.google.com/p/modwsgi/wiki/ApplicationIssues#Application_Environment_Variables
    * https://github.com/twoscoops/django-twoscoops-project/issues/60#issuecomment-25935406

Instead, we are using a private configuration file that MUST not be
added to the git repository to protect private configuration data.
"""

from base import *  # noqa

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured

try:
    import prod_private
except ImportError:
    raise ImproperlyConfigured("Create a prod_private.py file in settings")


def get_prod_setting(setting):
    """Get the setting or return exception """
    try:
        return getattr(prod_private, setting)
    except AttributeError:
        error_msg = "The %s setting is missing from prod settings" % setting
        raise ImproperlyConfigured(error_msg)


# Template configuration: enable compiled templates caching
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

INSTALLED_APPS += (
    'gunicorn',
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
