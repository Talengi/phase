# -*- coding: utf-8 -*-



import factory
from factory import fuzzy

from discussion.models import Note


class NoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Note

    body = fuzzy.FuzzyText()
