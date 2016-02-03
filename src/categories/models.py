# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string
import random

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from tools.models import SlugManager
from documents.forms.models import documentform_factory


class Organisation(models.Model):
    objects = SlugManager()

    name = models.CharField(
        _('Name'),
        max_length=50)
    slug = models.SlugField(
        _('Slug'),
        max_length=50)
    trigram = models.CharField(
        _('Trigram'),
        max_length=3,
        unique=True)
    description = models.CharField(
        _('Description'),
        max_length=200,
        null=True, blank=True)

    class Meta:
        app_label = 'categories'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.trigram:
            self.trigram = self.random_trigram()
        super(Organisation, self).save(*args, **kwargs)

    def random_trigram(self):
        """Returns a word of three random letters."""
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(3))


class CategoryTemplate(models.Model):
    objects = SlugManager()

    name = models.CharField(
        _('Name'),
        max_length=50)
    slug = models.SlugField(
        _('Slug'),
        max_length=50)
    description = models.CharField(
        _('Description'),
        max_length=200,
        null=True, blank=True)
    use_creation_form = models.BooleanField(
        _('Use document creation form'),
        default=True)

    # We use a generic foreign key to reference
    # the type of document metadata this category
    # will host.
    metadata_model = models.ForeignKey(ContentType)

    class Meta:
        verbose_name = _('Category template')
        verbose_name_plural = _('Category templates')
        app_label = 'categories'

    def __unicode__(self):
        return self.name


class CategoryManager(models.Manager):
    def get_by_natural_key(self, organisation_slug, category_slug):
        return self.get(organisation__slug=organisation_slug,
                        category_template__slug=category_slug)


class Category(models.Model):
    """Link between organisation / category and users and groups."""
    objects = CategoryManager()

    organisation = models.ForeignKey(
        Organisation,
        related_name='categories',
        verbose_name=_('Organisation'))
    category_template = models.ForeignKey(
        CategoryTemplate,
        verbose_name=_('Category template'))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='categories',
        blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='owner_groups')
    third_parties = models.ManyToManyField(
        'accounts.Entity',
        blank=True,
        related_name='linked_categories')

    class Meta:
        unique_together = ('category_template', 'organisation')
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return '%s > %s' % (self.organisation.name,
                            self.category_template.name)

    @property
    def name(self):
        return self.category_template.name

    @property
    def slug(self):
        return self.category_template.slug

    @property
    def use_creation_form(self):
        return self.category_template.use_creation_form

    def document_class(self):
        Model = self.category_template.metadata_model
        return Model.model_class()

    def revision_class(self):
        return self.document_class().get_revision_class()

    def get_metadata_form_class(self):
        return documentform_factory(self.document_class())

    def get_revision_form_class(self):
        return documentform_factory(self.revision_class())

    def document_type(self):
        return '{}.{}'.format(
            self.organisation.slug, self.category_template.slug)

    def get_absolute_url(self):
        url = reverse('category_document_list', args=(
            self.organisation.slug,
            self.category_template.slug))
        return url

    def get_transmittal_columns(self):
        """Lists columns that must be in the transmittal csv."""
        return self.document_class().PhaseConfig.transmittal_columns

    def get_download_url(self):
        """Gets the url used to download a list of documents."""
        url = reverse('document_download', args=(
            self.organisation.slug,
            self.category_template.slug))
        return url


class Contract(models.Model):
    number = models.CharField(_('Number'), max_length=50)
    name = models.CharField(_('Name'), max_length=255)
    categories = models.ManyToManyField(Category,
                                        related_name='contracts',
                                        verbose_name=_('Categories'))

    def __unicode__(self):
        return self.number
