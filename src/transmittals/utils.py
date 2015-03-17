# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class FieldWrapper(object):
    """Utility class to access fields scattered across multiple objects."""

    def __init__(self, objects):
        self.objects = objects

    def __getitem__(self, attr):
        it = iter(self.objects)

        try:
            obj = it.next()
            while not hasattr(obj, attr):
                obj = it.next()
            return getattr(obj, attr)
        except StopIteration:
            raise AttributeError('Attribute {} not found'.format(attr))

    def __getattr__(self, attr):
        return self[attr]
