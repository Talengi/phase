from django.db import models
from django.utils.translation import ugettext_lazy as _


class ValuesList(models.Model):
    """Administrable key / value list to use in Choices fields."""
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

    def __unicode__(self):
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

    def __unicode__(self):
        return '%s - %s' % (self.index, self.value)
