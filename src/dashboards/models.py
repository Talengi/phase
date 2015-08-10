# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from categories.models import Category
from dashboards.fields import DashboardProviderChoiceField


class Dashboard(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'))
    data_provider = DashboardProviderChoiceField(_('Dashboard data provider'))
