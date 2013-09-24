from django.test import TestCase

from accounts.factories import UserFactory


class NavbarTests(TestCase):
    """Navbar shows different options depending on user's permissions."""

    def setUp(self):
        self.user = UserFactory(name='User', password='pass')
        self.url = '/'

    def test_anonymous_navbar(self):
        res = self.client.get(self.url, follow=True)
        self.assertNotContains(res, 'href="/favorites/"')
        self.assertNotContains(res, 'href="/">Documents')
        self.assertNotContains(res, 'href="/create/"')
        self.assertNotContains(res, 'href="/admin/"')

    def test_authenticated_user_navbar(self):
        self.client.login(username=self.user.email, password='pass')
        self.assertTrue(self.user.is_authenticated())

        res = self.client.get(self.url, follow=True)
        self.assertContains(res, 'href="/favorites/"')
        self.assertContains(res, 'href="/">Documents')
        self.assertNotContains(res, 'href="/create/"')
        self.assertNotContains(res, 'href="/admin/"')

    def test_admin_navbar(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username=self.user.email, password='pass')
        self.assertTrue(self.user.is_authenticated())

        res = self.client.get(self.url, follow=True)
        self.assertContains(res, 'href="/favorites/"')
        self.assertContains(res, 'href="/">Documents')
        self.assertContains(res, 'href="/create/"')
        self.assertContains(res, 'href="/admin/"')


class AclTests(TestCase):
    pass
