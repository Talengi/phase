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

ELASTIC_INDEX = 'test_documents'
ELASTIC_AUTOINDEX = False
CELERY_ALWAYS_EAGER = True

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

TRS_IMPORTS_ROOT = Path('/tmp/test_ctr_clt')

TRS_IMPORTS_CONFIG = {
    'test': {
        'INCOMING_DIR': TRS_IMPORTS_ROOT.child('incoming'),
        'REJECTED_DIR': TRS_IMPORTS_ROOT.child('rejected'),
        'TO_BE_CHECKED_DIR': TRS_IMPORTS_ROOT.child('tobechecked'),
        'ACCEPTED_DIR': TRS_IMPORTS_ROOT.child('accepted'),
    }
}
