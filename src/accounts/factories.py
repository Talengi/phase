import factory

from accounts.models import User


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    email = factory.Sequence(lambda n: 'test{0}@phase.fr'.format(n))
    name = factory.Sequence(lambda n: 'User {0}'.format(n))
    password = '1234'

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user
