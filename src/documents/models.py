# -*- coding: utf-8 -*-

import zipfile
import tempfile
from collections import OrderedDict

from django.db import models
from django.db.models.base import ModelBase
from django.utils import timezone, six
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from annoying.functions import get_object_or_None

from accounts.models import User
from documents.fields import RevisionFileField
from categories.models import Category
from documents.templatetags.documents import MenuItem, DividerMenuItem


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
    document_number = models.CharField(
        _('Document number'),
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
        blank=True)
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
        # Permission used in sidebar template to check if user belongs to
        # doc controller group
        permissions = (('can_control_document', 'Can control document'),)

    def __unicode__(self):
        return self.document_number

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

    def get_edit_url(self, revision=None):
        kwargs = {
            'organisation': self.category.organisation.slug,
            'category': self.category.category_template.slug,
            'document_key': self.document_key
        }
        if revision is not None:
            kwargs.update({'revision': revision})

        url = reverse('document_edit', kwargs=kwargs)
        return url

    def get_revise_url(self):
        url = reverse('document_revise', args=(
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
        return self.get_latest_revision().to_json()

    def document_type(self):
        return self.category.document_type()


# TODO Add the "latest_revision" test
class MetadataBase(ModelBase):
    """Custom metaclass for Metadata.

    Validates that all classes inheriting from Metadata
    define all the required fields.

    An optional `filter_fields_order` defines the order in which right sidebar
    filter fields are displayed.
    """
    def __new__(cls, name, bases, attrs):
        if name != 'NewBase' and name != 'Metadata':
            base_attrs = []
            for base in bases:
                if hasattr(base, '_meta'):
                    base_attrs += base._meta.fields

            phase_config = attrs.get('PhaseConfig', None)
            if not phase_config:
                raise TypeError('You are missing the "PhaseConfig" configuration '
                                'class on %s' % name)

            filter_fields = getattr(phase_config, 'filter_fields', None)
            column_fields = getattr(phase_config, 'column_fields', None)
            filter_fields_order = getattr(
                phase_config, 'filter_fields_order', None)

            if not all((filter_fields, column_fields)):
                raise TypeError('Your "PhaseConfig" definition is incorrect '
                                'on %s. Please check the doc' % name)

            if filter_fields_order:
                if not set(filter_fields) <= set(filter_fields_order):
                    raise TypeError(
                        'Your "PhaseConfig" definition is incorrect '
                        '"filter_fields_order" should contain the same '
                        'elements as "filter_fields" and the base'
                        ' visible fields from'
                        ' "documents.forms.BaseDocumentFilterForm"')

        return super(MetadataBase, cls).__new__(cls, name, bases, attrs)


class Metadata(six.with_metaclass(MetadataBase, models.Model)):
    document = models.OneToOneField(Document)
    document_key = models.SlugField(
        _('Document key'),
        blank=True,
        unique=True,
        db_index=True,
        max_length=250)
    document_number = models.CharField(
        _('Document number'),
        blank=True,
        max_length=250)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.document_key

    def get_absolute_url(self):
        return self.document.get_absolute_url()

    def save(self, *args, **kwargs):
        """Make sure the document has a document key."""
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
            .select_related() \
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

    @classmethod
    def get_batch_actions(cls, category, user):
        """Define actions that apply on lists of documents.

        This list is used to build the menu in the document list navbar.

        """
        actions = OrderedDict()
        actions['download'] = MenuItem(
            'download',
            _('Download'),
            reverse('document_download', args=[
                category.organisation.slug,
                category.slug]),
            ajax=False,
            modal='documents-download-modal',
            icon='download')
        return actions

    @classmethod
    def get_batch_actions_modals(cls):
        """Returns a list of templates used in batch actions."""
        return ['documents/document_list_download_modal.html']

    @classmethod
    def get_document_download_form(cls, data, queryset):
        from documents.forms.utils import DocumentDownloadForm
        return DocumentDownloadForm(data, queryset=queryset)

    @classmethod
    def compress_documents(cls, documents, **kwargs):
        """Compress the given files' documents (or queryset) in a zip file.

        * format can be either 'both', 'native' or 'pdf'
        * revisions can be either 'latest' or 'all'

        Returns the name of the ziped file.
        """
        format = kwargs.pop('format', 'both')
        revisions = kwargs.pop('revisions', 'latest')
        temp_file = tempfile.TemporaryFile()

        with zipfile.ZipFile(temp_file, mode='w') as zip_file:
            files = []
            for document in documents:
                if revisions == 'latest':
                    revs = [document.latest_revision]
                elif revisions == 'all':
                    revs = document.get_all_revisions()

                for rev in revs:
                    if rev is not None:
                        if format in ('native', 'both'):
                            files.append(rev.native_file)
                        if format in ('pdf', 'both'):
                            files.append(rev.pdf_file)

            for file_ in files:
                if file_.name:
                    zip_file.write(
                        file_.path,
                        file_.name,
                        compress_type=zipfile.ZIP_DEFLATED
                    )
        return temp_file


class MetadataRevision(models.Model):
    document = models.ForeignKey(Document)

    revision = models.PositiveIntegerField(_('Revision'))
    revision_date = models.DateField(
        null=True, blank=True,
        verbose_name=u"Revision Date")
    native_file = RevisionFileField(
        verbose_name=u"Native File",
        null=True, blank=True, max_length=255)
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

    def get_first_revision_number(self):
        """The default value for the "revision" field.

        This method is called in `documents.utils.create_document_from_forms`
        to set the value of the first revision number (self.revision).

        We cannot define a default callable directly on the field, because we
        would not be able to override the default value in MetadataRevision
        subclasses.

        """
        return 0

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
    def revision_name(self):
        return self.name

    @property
    def unique_id(self):
        return self.id

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
        column_fields = dict(config.column_fields).values()
        indexable_fields = getattr(config, 'indexable_fields', [])
        fields_to_index = set(filter_fields + column_fields + indexable_fields)

        for field in fields_to_index:
            fields += add_to_fields(field)

        fields_infos = dict(fields)
        fields_infos.update({
            u'url': document.get_absolute_url(),
            u'document_key': document.document_key,
            u'document_number': document.document_number,
            u'document_pk': document.pk,
            u'metadata_pk': metadata.pk,
            u'pk': self.pk,
            u'revision': self.revision,
            u'is_latest_revision': document.current_revision == self.revision,
        })
        return fields_infos

    def get_initial_ignored_fields(self):
        """New revision initial data that must stay default."""
        fields_to_ignore = (
            'created_on', 'status', 'native_file', 'pdf_file', 'received_date'
        )
        return fields_to_ignore

    def get_initial_empty(self):
        """New revision initial data that must be empty."""
        empty_fields = ('revision_date', 'status', 'final_revision')
        return empty_fields

    def get_new_revision_initial(self, form):
        """Gets the initial data that must be passed to the new revision form.

        We want all the fields to be blank, so we need to get rid of default
        values.

        """
        # Build an array of initial data from current fields
        fields = form.fields.keys()
        initial_data = dict(map(lambda x: (x, getattr(self, x, None)), fields))

        initial_ignored = self.get_initial_ignored_fields()
        for field in initial_ignored:
            if field in initial_data:
                del initial_data[field]

        initial_empty = self.get_initial_empty()
        for field in initial_empty:
            if field in initial_data:
                initial_data[field] = None

        return initial_data

    def post_trs_import(self, trs_revision):
        """Custom hook called after creation from a Transmittal.

        When a `transmittals.models.Transmittal` is imported, the
        `transmittals.models.TrsRevision` object creates or updates the
        document and revisions. Sometimes, we whant to perform additionals
        actions, e.g creating the `reviews.models.Review` objects. That's why
        we need this custom hook.

        """
        pass

    def detail_view_context(self, request):
        """Return values to inject in the view context.

        Some documents might want to inject additional values in
        the document detail template context.
        """
        return {}

    def get_actions(self, metadata, user):
        """Define actions that apply to a single document.

        This list is used to builde the "Actions" menu in the
        document form.

        """
        actions = []
        category = self.document.category

        if user.has_perm('can_change_document'):
            actions.append(MenuItem(
                'create-revision',
                _('Create revision'),
                reverse('document_revise', args=[
                    category.organisation.slug,
                    category.slug,
                    self.document.document_key]),
                disabled=self.is_under_review(),
                method='GET',
            ))

        if user.has_perm('can_control_document'):
            actions.append(DividerMenuItem())

            actions.append(MenuItem(
                'delete-revision',
                _('Delete last revision'),
                reverse('document_revision_delete', args=[
                    category.organisation.slug,
                    category.slug,
                    self.document.document_key]),
                modal='delete-revision-modal',
                disabled=self.revision <= 1
            ))

            actions.append(MenuItem(
                'delete-document',
                _('Delete document'),
                reverse('document_delete', args=[
                    category.organisation.slug,
                    category.slug,
                    self.document.document_key]),
                modal='delete-document-modal'
            ))

        return actions

    def get_action_modals(self):
        return [
            'documents/document_detail_delete_revision_modal.html',
            'reviews/document_detail_cancel_review_modal.html',
            'reviews/document_detail_start_review_with_comments.html',
        ]
