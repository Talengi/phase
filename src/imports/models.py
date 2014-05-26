from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import UUIDField

from documents.models import Document


class ImportBatch(models.Model):
    uid = UUIDField(primary_key=True)


class Import(models.Model):
    batch = models.ForeignKey(
        ImportBatch,
        verbose_name=_('Batch')
    )
    document = models.ForeignKey(
        Document,
        null=True, blank=True
    )
