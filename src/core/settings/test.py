from base import *  # noqa


########## IN-MEMORY TEST DATABASE
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
REVISION_FILES_ROOT = MEDIA_ROOT
