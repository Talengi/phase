from base import *  # noqa


# ######### IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

# We need a different media root so we can wipe it securely in tests
MEDIA_ROOT = '/tmp/phase_media/'

PIPELINE_ENABLED = False
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

ELASTIC_AUTOINDEX = False

LOGGING['loggers']['elasticsearch'] = {
    'handlers': ['console', 'syslog', 'mail_admins'],
    'level': 'ERROR',
    'propagate': False,
}

LOGGING['loggers']['elasticsearch.trace'] = {
    'handlers': ['console', 'syslog', 'mail_admins'],
    'level': 'ERROR',
    'propagate': False,
}
