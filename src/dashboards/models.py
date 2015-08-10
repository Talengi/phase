# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from dashboards.fields import DashboardProviderChoiceField


class Dashboard(models.Model):
    slug = models.SlugField(
        _('Slug'),
        unique=True,
        db_index=True,
        max_length=250)
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'))
    data_provider = DashboardProviderChoiceField(
        _('Dashboard data provider'))
