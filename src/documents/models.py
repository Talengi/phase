#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.urlresolvers import reverse

from accounts.models import User
from categories.models import Category
from documents.utils import stringify_value


class DocumentManager(models.Manager):
    def get_by_natural_key(self, document_key):
        return self.get(document_key=document_key)


class Document(models.Model):
    """A single document base model."""
    objects = DocumentManager()

    document_key = models.SlugField(
        _('Document number'),
        unique=True,
        db_index=True,
        max_length=250)
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'),
        related_name='documents')
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)
    updated_on = models.DateTimeField(
        _('Updated on'),
        default=timezone.now)
    favorited_by = models.ManyToManyField(
        User,
        through='favorites.Favorite',
        null=True, blank=True)
    current_revision = models.PositiveIntegerField(
        verbose_name=u"Revision")
    current_revision_date = models.DateField(
        verbose_name=u"Revision Date")

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

    def get_absolute_url(self):
        """Get the document url.

        If the category is already in cache, we return the full url.

        Otherwise, we return the short url to prevent a useless query.

        """
        if hasattr(self, '_category_cache'):
            url = reverse('document_detail', args=[
                self.category.organisation.slug,
                self.category.slug,
                self.document_key
            ])
        else:
            url = reverse('document_short_url', args=[self.document_key])

        return url

    def get_edit_url(self):
        url = reverse('document_edit', args=(
            self.category.organisation.slug,
            self.category.category_template.slug,
            self.document_key,
        ))
        return url

    def natural_key(self):
        # You MUST return a tuple here to prevent this bug
        # https://code.djangoproject.com/ticket/13834
        return (self.document_key,)

    @property
    def metadata(self):
        """Returns the metadata object."""
        Model = self.category.category_template.metadata_model
        metadata = Model.get_object_for_this_type(document=self)
        return metadata


class Metadata(models.Model):
    document = models.ForeignKey(
        Document,
        unique=True)
    document_key = models.SlugField(
        _('Document number'),
        unique=True,
        db_index=True,
        max_length=250)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.document_key

    def get_absolute_url(self):
        return self.document.get_absolute_url()

    def save(self, *args, **kwargs):
        """Make sure the document has a document key."""
        if not self.document_key:
            self.document_key = self.generate_document_key()
        super(Metadata, self).save(*args, **kwargs)

        self.document.updated_on = timezone.now()
        self.document.current_revision = self.latest_revision.revision
        self.document.current_revision_date = self.latest_revision.updated_on
        self.document.save()

    def generate_document_key(self):
        """Returns a uniquely identifying key."""
        raise NotImplementedError()

    def get_revision_class(self):
        """Return the class of the associated revision model."""
        return self._meta.get_field('latest_revision').rel.to

    def get_all_revisions(self):
        """Return all revisions data of this document."""
        Revision = self.get_revision_class()
        revisions = Revision.objects \
            .filter(document=self.document) \
            .select_related('document')
        return revisions

    def get_revision(self, revision):
        """Returns the rivision with the specified number."""
        Revision = self.get_revision_class()
        revision = Revision.objects \
            .filter(document=self.document) \
            .select_related('document') \
            .get(revision=revision)
        return revision

    def natural_key(self):
        """Returns the natural unique key of the document.

        This must be useable in a url.
        """
        raise NotImplementedError()

    def jsonified(self, document2favorite={}):
        """Returns a list of document values ready to be json-encoded.

        The first element of the list is the linkified document number.
        """
        favorited = self.document.pk in document2favorite.keys()

        fields = tuple()
        for field in self.PhaseConfig.column_fields:
            key = field[1]
            # TODO Use field[2] for getting field value
            value = getattr(self, field[1])
            fields += ((key, stringify_value(value)),)

        fields_infos = dict(fields)
        fields_infos.update({
            'url': self.document.get_absolute_url(),
            'number': self.natural_key(),
            'pk': self.pk,
            'document_pk': self.document.pk,
            'favorite_id': document2favorite.get(self.document.pk, ''),
            'favorited': favorited,
        })
        return fields_infos

    @property
    def current_revision(self):
        return '%(revision)02d' % {'revision': self.latest_revision.revision}

    @property
    def current_revision_date(self):
        return self.latest_revision.created_on


class MetadataRevision(models.Model):
    document = models.ForeignKey(Document)

    revision = models.PositiveIntegerField(
        verbose_name=u"Revision",
        default=1)
    revision_date = models.DateField(
        default=timezone.now,
        verbose_name=u"Revision Date")
    created_on = models.DateField(
        _('Created on'),
        default=timezone.now)
    updated_on = models.DateTimeField(
        _('Updated on'),
        auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-revision',)
        get_latest_by = 'revision'
        unique_together = ('document', 'revision')
