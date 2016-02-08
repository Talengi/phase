# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.core.files.storage import FileSystemStorage
from django.conf import settings


protected_storage = FileSystemStorage(
    location='{}'.format(settings.PROTECTED_ROOT),
    base_url='{}'.format(settings.PROTECTED_URL))

private_storage = FileSystemStorage(
    location='{}'.format(settings.PRIVATE_ROOT),
    base_url='{}'.format(settings.PRIVATE_URL))
