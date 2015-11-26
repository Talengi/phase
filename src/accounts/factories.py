# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory

from categories.factories import CategoryFactory
from accounts.models import User, Entity


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'test{0}@phase.fr'.format(n))
    username = factory.Sequence(lambda n: 'test{0}'.format(n))
    name = factory.Sequence(lambda n: 'User {0}'.format(n))
    password = '1234'

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        category = kwargs.pop('category', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()

        # Users MUST belong to at least one category
        if not category:
            category = CategoryFactory()
        category.users.add(user)

        return user


class EntityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Entity

    name = factory.fuzzy.FuzzyText(length=20)
    trigram = factory.fuzzy.FuzzyText(length=3)
