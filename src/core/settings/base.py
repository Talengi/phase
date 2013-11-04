"""Common settings and globals."""


from os.path import basename, join, normpath
from sys import path
from unipath import Path
from logging.handlers import SysLogHandler


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = Path(__file__).ancestor(3)

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = DJANGO_ROOT.ancestor(1)

# Site name:
SITE_NAME = basename(SITE_ROOT)

# Path to the project Configuration app
CONFIGURATION_APP_ROOT = Path(__file__).ancestor(2)

# Path to public files (served by the web server)
PUBLIC_ROOT = SITE_ROOT.child('public')

# Path to private files (must be served with X-SENDFILE)
PRIVATE_ROOT = SITE_ROOT.child('private')

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
path.append(CONFIGURATION_APP_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Matthieu Lamy', 'matthieu@talengi.fr'),
    ('Thibault Jouannic', 'thibault@jouannic.fr'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'phase.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/Los_Angeles'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = PUBLIC_ROOT.child('media')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = PUBLIC_ROOT.child('static')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    DJANGO_ROOT.child('static'),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = r"This is a dummy secret key!"
########## END SECRET CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    DJANGO_ROOT.child('fixtures'),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'accounts.context_processors.navigation',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    DJANGO_ROOT.child('templates'),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Performance middlewares
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',

    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Custom middlewares
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'core.urls'
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

THIRD_PARTY_APPS = (
    # Database migration helpers:
    'south',
    'pipeline',
    'widget_tweaks',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'documents',
    'bootstrap',
    'accounts',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See http://www.miximum.fr/bien-developper/876-an-effective-logging-strategy-with-django
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[phase] %(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        # Send all messages to console
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        # Send info messages to syslog
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'facility': SysLogHandler.LOG_LOCAL2,
            'address': '/dev/log',
            'formatter': 'verbose',
        },
        # Warning messages are sent to admin emails
        'mail_admins': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        # critical errors are logged to sentry
        #'sentry': {
        #    'level': 'ERROR',
        #    'filters': ['require_debug_false'],
        #    'class': 'raven.contrib.django.handlers.SentryHandler',
        #},
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console', 'syslog', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION

########## PIPELINE CONFIGURATION
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'base': {
        'source_filenames': (
            'css/phase-bootstrap.css',
            'css/jquery-ui.css',
            # must be loaded after jquery-ui js to avoid conflicts
            'css/datepicker.css',
            'css/project.css',
        ),
        'output_filename': 'css/base.css',
    },
    'detail': {
        'source_filenames': (
            'css/jquery.multiselect.css',
            'css/jquery.multiselect.filter.css',
        ),
        'output_filename': 'css/detail.css',
    },
}

PIPELINE_JS = {
    'base': {
        'source_filenames': (
            'js/jquery.js',
            'js/jquery-ui.min.js',
            # both bootstrap and bootstrap-datepicker must be loaded
            # after jquery-ui js to avoid conflicts
            'js/phase-bootstrap.js',
            'js/bootstrap-datepicker.js',
        ),
        'output_filename': 'js/base.js',
    },
    'list': {
        'source_filenames': (
            'js/jquery.afterkeyup.js',
            'js/document-list.js',
        ),
        'output_filename': 'js/list.js',
    },
    'detail': {
        'source_filenames': (
            'js/jquery.multiselect.js',
            'js/jquery.multiselect.filter.js',
            'js/document-detail.js',
        ),
        'output_filename': 'js/detail.js',
    },
    'datatable': {
        'source_filenames': (
            'js/templayed.js',
            # must be loaded after templayed js
            'js/jquery.datatable.js',
            'js/jquery.favbystar.js',
            'js/jquery.infinitescroll.js',
            'js/queryparams.js',
            'js/jquery.inview.js',
        ),
        'output_filename': 'js/datatable.js',
    },
}
########## END PIPELINE CONFIGURATION

########## EMAIL CONFIGURATION
DEFAULT_FROM_EMAIL = 'admin@phase.fr'
########## END EMAIL CONFIGURATION

########## CUSTOM CONFIGURATION
PAGINATE_BY = 50  # Document list pagination
CACHE_TIMEOUT_SECONDS = 300  # seconds == 5 minutes
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'

# Where should revisions' files go
REVISION_FILES_ROOT = PRIVATE_ROOT.child('documents')
REVISION_FILES_URL = '/documents/'
USE_X_SENDFILE = DEBUG
########## END CUSTOM CONFIGURATION
