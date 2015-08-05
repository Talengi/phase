# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class SlugManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.slug_field = kwargs.pop('slug_field', 'slug')
        super(SlugManager, self).__init__(*args, **kwargs)

    def get_by_natural_key(self, slug):
        return self.get(**{self.slug_field: slug})
