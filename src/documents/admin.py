#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.sites.models import Site


# Unregister useless default admin modules
admin.site.unregister(Site)
