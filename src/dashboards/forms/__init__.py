# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def classpath(klass):
    return '{}.{}'.format(
        klass.__module__, klass.__name__)
