# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import factory

from discussion.models import Note


class NoteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Note

    body = factory.fuzzy.FuzzyText()
