from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.factories import UserFactory, MembershipFactory


class UserCreationTests(TestCase):
    def setUp(self):
        self.url = reverse('admin:accounts_user_add')

        self.user = UserFactory(
            name='Admin',
            password='pass',
            is_staff=True,
            is_superuser=True)
        self.client.login(username=self.user.email, password='pass')

    def test_creating_user_requires_category(self):
        """Validation of required inlines.

        When a user is created, the admin MUST select at least
        a document category to be linked.

        """
        data = {
            'email': 'test@testing.com',
            'name': 'Test',
            'password1': 'password',
            'password2': 'password',
            'CategoryMembership_users-INITIAL_FORMS': 0,
            'CategoryMembership_users-TOTAL_FORMS': 0,
        }
        res = self.client.post(self.url, data)
        self.assertContains(res, 'Please select at least one category')

    def test_updating_user_requires_category(self):
        """Validation of required inlines.

        When a user is updated, the admin MUST select at least
        a document category to be linked.

        """
        user = UserFactory()
        url = reverse('admin:accounts_user_change', args=[user.id])
        data = {
            'email': 'test@testing.com',
            'name': 'Test',
            'password1': 'password',
            'password2': 'password',
            'CategoryMembership_users-INITIAL_FORMS': 0,
            'CategoryMembership_users-TOTAL_FORMS': 0,
        }
        res = self.client.post(url, data)
        self.assertContains(res, 'Please select at least one category')

    def test_updating_user_with_category_deletion(self):
        """Validation of required inlines.

        When a user is updated, one can require category deletions. We MUST
        make sure that there is always one category left.

        """
        user = UserFactory()
        membership = MembershipFactory()
        membership.users.add(user)
        membership.save()

        url = reverse('admin:accounts_user_change', args=[user.id])
        data = {
            'email': 'test@testing.com',
            'name': 'Test',
            'password1': 'password',
            'password2': 'password',
            'CategoryMembership_users-INITIAL_FORMS': 1,
            'CategoryMembership_users-MAX_NUM_FORMS': 1000,
            'CategoryMembership_users-TOTAL_FORMS': 1,
            'CategoryMembership_users-0-DELETE': 1,
            'CategoryMembership_users-0-id': membership.id,
            'CategoryMembership_users-0-user': user.id,
        }
        res = self.client.post(url, data)
        self.assertContains(res, 'Please select at least one category')
