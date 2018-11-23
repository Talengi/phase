# -*- coding: utf-8 -*-


import factory

from categories.factories import CategoryFactory
from accounts.models import User, Entity


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'test{0:03d}@phase.fr'.format(n))
    username = factory.Sequence(lambda n: 'test{0:03d}'.format(n))
    name = factory.Sequence(lambda n: 'User {0:03d}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', '1234')

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            extracted.users.add(self)
        else:
            category = CategoryFactory()
            category.users.add(self)


class EntityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Entity

    name = factory.fuzzy.FuzzyText(length=20)
    trigram = factory.fuzzy.FuzzyText(length=3)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)
