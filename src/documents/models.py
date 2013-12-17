#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from metadata.fields import ConfigurableChoiceField
from accounts.models import User
from categories.models import Category
from documents.constants import REVISIONS


class DocumentManager(models.Manager):
    def get_by_natural_key(self, document_key):
        return self.get(document_key=document_key)


class Document(models.Model):
    """A single document base model."""
    objects = DocumentManager()

    document_key = models.SlugField(
        _('Document key'),
        unique=True,
        db_index=True,
        max_length=250)
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'),
        related_name='documents')
    created_on = models.DateField(
        _('Created on'),
        auto_now_add=True)
    updated_on = models.DateTimeField(
        _('Updated on'),
        auto_now=True)
    favorited_by = models.ManyToManyField(
        User,
        through='favorites.Favorite',
        null=True, blank=True)
    current_revision = ConfigurableChoiceField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        list_index='REVISIONS')
    current_revision_date = models.DateField(
        verbose_name=u"Revision Date")

    metadata_type = models.ForeignKey(ContentType)
    metadata_id = models.PositiveIntegerField()
    metadata = generic.GenericForeignKey('metadata_type', 'metadata_id')

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __unicode__(self):
        return self.document_key

    def save(self, *args, **kwargs):
        if self.pk is None:
            # This is a document creation
            # TODO get document key from metadata object
            # TODO get fields required for favorites management
            pass
        super(Document, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('document_short_url', [
            self.document_key,
        ])

    def natural_key(self):
        # You MUST return a tuple here to prevent this bug
        # https://code.djangoproject.com/ticket/13834
        return (self.document_key,)


class Metadata(models.Model):
    document = models.ForeignKey(
        Document,
        unique=True)
    document_key = models.SlugField(
        _('Document key'),
        unique=True,
        db_index=True,
        max_length=250)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.natural_key()

    def get_absolute_url(self):
        return self.document.get_absolute_url()

    def natural_key(self):
        """Returns the natural unique key of the document.

        This must be useable in a url.
        """
        raise NotImplementedError()

    def jsonified(self, document2favorite={}):
        """Returns a list of document values ready to be json-encoded.

        The first element of the list is the linkified document number.
        """
        favorited = self.pk in document2favorite.keys()
        fields_infos = dict((field[1], unicode(getattr(self, field[1])))
                            for field in self.PhaseConfig.column_fields)
        fields_infos.update({
            u'url': self.document.get_absolute_url(),
            u'number': self.natural_key(),
            u'pk': self.pk,
            u'favorite_id': document2favorite.get(self.pk, u''),
            u'favorited': favorited,
        })
        return fields_infos


class MetadataRevision(models.Model):
    document = models.ForeignKey(Document)

    revision = models.CharField(
        verbose_name=u"Revision",
        default=u"00",
        max_length=2,
        choices=REVISIONS)
    revision_date = models.DateField(
        auto_now_add=True,
        verbose_name=u"Revision Date")
    created_on = models.DateField(
        _('Created on'),
        auto_now_add=True)
    updated_on = models.DateTimeField(
        _('Updated on'),
        auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-revision',)
        get_latest_by = 'revision'
