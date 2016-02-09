# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.core.files.storage import FileSystemStorage
from django.conf import settings


class ProtectedStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'location': '{}'.format(settings.PROTECTED_ROOT),
            'base_url': '{}'.format(settings.PROTECTED_URL)
        })
        super(ProtectedStorage, self).__init__(*args, **kwargs)


class PrivateStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'location': '{}'.format(settings.PRIVATE_ROOT),
            'base_url': '{}'.format(settings.PRIVATE_URL)
        })
        super(PrivateStorage, self).__init__(*args, **kwargs)


# We had to override `FileSystemStorage` instead of just instanciating it
# with the correct parameters because those parameters were ending up in
# the migrations file, with paths that only existed on the machine that
# generated the migration.
protected_storage = ProtectedStorage()
private_storage = PrivateStorage()
