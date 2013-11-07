from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from documents.models import Document


class Organisation(models.Model):
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

    def __unicode__(self):
        return self.name


class CategoryTemplate(models.Model):
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

    # We use a generic foreign key to reference
    # the type of document metadata this category
    # will host.
    metadata_model = models.ForeignKey(ContentType)

    class Meta:
        verbose_name = _('Category template')
        verbose_name_plural = _('Category templates')

    def __unicode__(self):
        return self.name


class Category(models.Model):
    """Link between organisation / category and users and groups."""
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
        null=True, blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        null=True, blank=True)
    documents = models.ManyToManyField(
        Document,
        related_name='categories',
        null=True, blank=True)

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

    def get_absolute_url(self):
        url = reverse('category_document_list', args=(
            self.organisation.slug,
            self.category_template.slug))
        return url
