from django.test import TestCase

from ..factories import UserFactory
from categories.factories import CategoryFactory


class UserFactoryTests(TestCase):
    """Test User Factory with differents configurations."""

    def test_user_factory(self):
        """Default generation, default category and password."""
        user = UserFactory(name='User')
        assert user.pk
        assert user.check_password('1234')  # default password
        assert user.categories.exists()  # default category is set

    def test_user_password_factory(self):
        """Generation with given password."""
        user = UserFactory(name='User', password='myownpass')
        assert user.check_password('myownpass')

    def test_user_category_factory(self):
        """Generation with given category."""
        my_category = CategoryFactory(organisation__name="my_org")

        user = UserFactory(name='User', category=my_category)
        assert user.categories.get().organisation.name == "my_org"
