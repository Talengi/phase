# -*- coding: utf-8 -*-


import logging

from django.conf import settings


class RequireSentryActivated(logging.Filter):
    def filter(self, record):
        return settings.USE_SENTRY
