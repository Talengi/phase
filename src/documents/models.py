# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, six
from django.core.urlresolvers import reverse
from annoying.functions import get_object_or_None

from accounts.models import User
from documents.fields import RevisionFileField
from categories.models import Category


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
    title = models.TextField(
        verbose_name=u"Title")
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
    is_indexable = models.BooleanField(
        _('Indexable'),
        default=True)
    current_revision = models.PositiveIntegerField(
        verbose_name=u"Revision")
    current_revision_date = models.DateField(
        null=True, blank=True,
        verbose_name=u"Revision Date")

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

        # Custom permission for document controllers
        permissions = (('can_control_document', 'Can control document'),)

    def __unicode__(self):
        return self.document_key

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
        """Old property name, kept for compatibility issues."""
        return self.get_metadata()

    def get_metadata(self):
        """Returns the metadata object.

        XXX WARNING XXX

        This method is a useful shortcut that makes tests writing easier.  It
        should not be used if it can be avoided because it's not optimal, since
        it generates a new query.

        """
        Model = self.category.category_template.metadata_model
        metadata = Model.get_object_for_this_type(document=self)
        return metadata

    @property
    def latest_revision(self):
        """Old property name, kept for compatibility issues."""
        return self.get_latest_revision()

    def get_latest_revision(self):
        """Returns the latest revision.

        XXX WARNING XXX

        See `get_metadata`
        """
        return self.get_metadata().latest_revision

    def get_revision_class(self):
        """Get the MetadataRevision subclass for this document."""
        return self.category.revision_class()

    def get_all_revisions(self):
        """Return all revisions data of this document."""
        RevisionClass = self.get_revision_class()
        revisions = RevisionClass.objects \
            .filter(document=self) \
            .select_related() \
            .order_by('-id')
        return revisions

    @property
    def current_revision_name(self):
        """A revision identifier should be displayed with two digits"""
        return u'%02d' % self.current_revision

    def to_json(self):
        return self.get_latest_revision.to_json()

    def document_type(self):
        return self.category.document_type()


# TODO Add the "latest_revision" test
class MetadataBase(ModelBase):
    """Custom metaclass for Metadata.

    Validates that all classes inheriting from Metadata
    define all the required fields.

    """
    def __new__(cls, name, bases, attrs):
        if name != 'NewBase' and name != 'Metadata':
            base_attrs = []
            for base in bases:
                base_attrs += base._meta.get_all_field_names()

            phase_config = attrs.get('PhaseConfig', None)
            if not phase_config:
                raise TypeError('You are missing the "PhaseConfig" configuration '
                                'class on %s' % name)

            filter_fields = getattr(phase_config, 'filter_fields', None)
            searchable_fields = getattr(phase_config, 'searchable_fields', None)
            column_fields = getattr(phase_config, 'column_fields', None)

            if not all((filter_fields, searchable_fields, column_fields)):
                raise TypeError('Your "PhaseConfig" definition is incorrect '
                                'on %s. Please check the doc' % name)

            if 'title' not in attrs and 'title' not in base_attrs:
                raise TypeError('You must define a title field or property '
                                'on model %s' % name)

        return super(MetadataBase, cls).__new__(cls, name, bases, attrs)


class Metadata(six.with_metaclass(MetadataBase), models.Model):
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
        self.document.title = self.title
        self.document.save()

    def generate_document_key(self):
        """Returns a uniquely identifying key."""
        raise NotImplementedError()

    @classmethod
    def get_revision_class(self):
        """Return the class of the associated revision model."""
        return self._meta.get_field('latest_revision').rel.to

    def get_all_revisions(self):
        """Return all revisions data of this document."""
        Revision = self.get_revision_class()
        revisions = Revision.objects \
            .filter(document=self.document) \
            .select_related('document') \
            .order_by('-id')
        return revisions

    def get_revision(self, revision):
        """Returns the rivision with the specified number."""
        Revision = self.get_revision_class()
        qs = Revision.objects \
            .filter(document=self.document) \
            .select_related('document')
        revision = get_object_or_None(qs, revision=revision)
        return revision

    def natural_key(self):
        """Returns the natural unique key of the document.

        This must be useable in a url.
        """
        raise NotImplementedError()

    @property
    def current_revision(self):
        return self.latest_revision.name

    @property
    def current_revision_date(self):
        return self.latest_revision.created_on


class MetadataRevision(models.Model):
    document = models.ForeignKey(Document)

    revision = models.PositiveIntegerField(
        verbose_name=u"Revision",
        default=0)
    revision_date = models.DateField(
        null=True, blank=True,
        verbose_name=u"Revision Date")
    native_file = RevisionFileField(
        verbose_name=u"Native File",
        null=True, blank=True)
    pdf_file = RevisionFileField(
        verbose_name=u"PDF File",
        null=True, blank=True)
    received_date = models.DateField(
        _('Received date'))
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

    def __unicode__(self):
        return '{} ({})'.format(
            self.document.document_key,
            self.revision)

    def save(self, update_document=False, *args, **kwargs):
        super(MetadataRevision, self).save(*args, **kwargs)

        if update_document:
            self.document.updated_on = timezone.now()
            self.document.save()

    def is_under_review(self):
        """This method is overriden in the ReviewMixin class."""
        return False

    @property
    def metadata(self):
        """Get the metadata object.

        TODO refactor to replace with a foreign key in each
        MetadataRevision subclass.

        """
        return self.document.get_metadata()

    @property
    def name(self):
        """A revision identifier should be displayed with two digits"""
        return u'%02d' % self.revision

    @property
    def unique_id(self):
        return '{}_{}'.format(self.document.document_key, self.name)

    def to_json(self):
        """Converts the revision to a json representation.

        Suitable for indexing in ES, for example.

        The first element of the list is the linkified document number.

        If a value is a Model instance (e.g a foreign key), we return both it's
        unicode and id values.
        """
        fields = tuple()
        document = self.document
        metadata = self.metadata

        def add_to_fields(key):
            # Search the value of `key` in the revision, metadata and document,
            # in that order. If not found, raise an exception.
            # Note that the value can be "None" so careful with have to
            # explicitely catch the AttributeError exception
            try:
                value = getattr(self, key)
            except AttributeError:
                try:
                    value = getattr(metadata, key)
                except AttributeError:
                    try:
                        value = getattr(document, key)
                    except AttributeError:
                        error = 'Cannot find field {} in doc {} ({})'.format(
                            key, document.document_key, document.document_type())
                        raise RuntimeError(error)

            if isinstance(value, models.Model):
                field = (
                    (unicode(key), value.__unicode__()),
                    (u'%s_id' % key, value.pk)
                )
            else:
                field = ((unicode(key), value),)

            return field

        config = metadata.PhaseConfig
        filter_fields = list(config.filter_fields)
        searchable_fields = list(config.searchable_fields)
        column_fields = dict(config.column_fields).values()
        additional_fields = getattr(config, 'indexable_fields', [])
        fields_to_index = set(filter_fields + searchable_fields + column_fields + additional_fields)

        for field in fields_to_index:
            fields += add_to_fields(field)

        fields_infos = dict(fields)
        fields_infos.update({
            'url': document.get_absolute_url(),
            'document_pk': document.pk,
            'metadata_pk': metadata.pk,
            'pk': self.pk,
            'revision': self.revision,
            'is_latest_revision': document.current_revision == self.revision,
        })
        return fields_infos
