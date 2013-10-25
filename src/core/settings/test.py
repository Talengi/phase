from base import *  # noqa


########## TEST SETTINGS
TEST_RUNNER = 'discover_runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = DJANGO_ROOT
TEST_DISCOVER_ROOT = DJANGO_ROOT
TEST_DISCOVER_PATTERN = "test_*.py"

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
