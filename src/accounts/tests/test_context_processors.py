from django.test import TestCase

from accounts.factories import UserFactory


class NavigationDataTest(TestCase):

    def setUp(self):
        self.user = UserFactory(name='User', password='pass')

    def test_anonymous_request(self):
        res = self.client.get('/', follow=True)
        self.assertNotIn('user_categories', res.context)

    def test_logged_request(self):
        self.client.login(username=self.user.email, password='pass')

        res = self.client.get('/', follow=True)
        self.assertIn('user_categories', res.context)
