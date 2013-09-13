#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group


# Unregister useless default admin modules
admin.site.unregister(Site)
admin.site.unregister(Group)
