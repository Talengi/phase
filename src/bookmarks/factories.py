import factory

from bookmarks.models import Bookmark


class BookmarkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Bookmark

    name = factory.Sequence(lambda n: 'Bookmark {0}'.format(n))
