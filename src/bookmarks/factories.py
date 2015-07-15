import factory

from bookmarks.models import Bookmark


class BookmarkFactory(factory.DjangoModelFactory):
    class Meta:
        model = Bookmark

    name = factory.Sequence(lambda n: 'Bookmark {0}'.format(n))
