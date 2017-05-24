from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.core.cache import cache


class IndexManager(models.Manager):
    def get_by_natural_key(self, index):
        return self.get(index=index)


class ValuesList(models.Model):
    """Administrable key / value list to use in Choices fields."""
    objects = IndexManager()

    index = models.CharField(
        _('Index'),
        max_length=50,
        db_index=True)
    name = models.CharField(
        _('Name'),
        max_length=255)

    class Meta:
        verbose_name = _('Values list')
        verbose_name_plural = _('Values lists')
        app_label = 'metadata'

    def __str__(self):
        return self.name


class ListEntry(models.Model):
    """Single entry in a values list."""
    values_list = models.ForeignKey(
        ValuesList,
        verbose_name=_('List'),
        related_name='values')
    order = models.PositiveIntegerField(
        _('Order'),
        default=0
    )
    index = models.CharField(
        _('Index'),
        max_length=50)
    value = models.CharField(
        _('Value'),
        max_length=1024,
        blank=True)

    class Meta:
        verbose_name = _('List entry')
        verbose_name_plural = _('List entries')
        ordering = ('order', 'index')
        app_label = 'metadata'

    def __str__(self):
        return '%s - %s' % (self.index, self.value)

    def save(self, *args, **kwargs):
        super(ListEntry, self).save(*args, **kwargs)
        cache.delete(self.values_list.index)
