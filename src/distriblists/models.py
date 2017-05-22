# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _
from accounts.models import User


class DistributionList(models.Model):
    name = models.CharField(
        _('Name'),
        max_length=250,
        unique=True)
    categories = models.ManyToManyField(
        'categories.Category',
        verbose_name=_('Category'))
    reviewers = models.ManyToManyField(
        User,
        verbose_name=_('Reviewers'),
        related_name='related_lists_as_reviewer',
        limit_choices_to={'is_external': False},
        blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='related_lists_as_leader',
        limit_choices_to={'is_external': False})
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='related_lists_as_approver',
        limit_choices_to={'is_external': False},
        null=True, blank=True)

    class Meta:
        app_label = 'distriblists'
        verbose_name = _('Distribution list')
        verbose_name_plural = _('Distribution lists')

    def __str__(self):
        return self.name
