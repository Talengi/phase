from base import *  # noqa


# ######### IN-MEMORY TEST DATABASE
SQLITE = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

PG = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'phase_test',
        'USER': 'phase',
        'PASSWORD': 'phase',
        'HOST': 'localhost',
        'PORT': '',
    }
}

DATABASES = PG

# We need a different media root so we can wipe it securely in tests
MEDIA_ROOT = '/tmp/phase_media/'
PRIVATE_ROOT = '/tmp/phase_media/'

PIPELINE_ENABLED = False
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

ELASTIC_INDEX = 'test_documents'
ELASTIC_AUTOINDEX = False

# Makes Celery working synchronously and in memory
CELERY_ALWAYS_EAGER = True
BROKER_URL = "memory://"
CELERY_CACHE_BACKEND = "memory"
CELERY_RESULT_BACKEND = "cache"

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
LOGGING['loggers'][''] = {
    'handlers': ['null'],
    'level': 'DEBUG',
    'propagate': False,
}

TRS_IMPORTS_ROOT = Path('/tmp/test_ctr_clt')

TRS_IMPORTS_CONFIG = {
    'test': {
        'INCOMING_DIR': TRS_IMPORTS_ROOT.child('incoming'),
        'REJECTED_DIR': TRS_IMPORTS_ROOT.child('rejected'),
        'TO_BE_CHECKED_DIR': TRS_IMPORTS_ROOT.child('tobechecked'),
        'ACCEPTED_DIR': TRS_IMPORTS_ROOT.child('accepted'),
        'EMAIL_LIST': ['test@phase.fr'],
    }
}
