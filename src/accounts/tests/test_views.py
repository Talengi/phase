from django.test import TestCase
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from accounts.factories import UserFactory


class NavbarTests(TestCase):
    """Navbar shows different options depending on user's permissions."""

    def setUp(self):
        category = CategoryFactory()
        self.user = UserFactory(name='User', password='pass', category=category)
        self.url = reverse('category_document_list', args=[
            category.organisation.slug,
            category.slug
        ])
        self.dc_perms = Permission.objects.filter(codename__endswith='_document')

    def test_anonymous_navbar(self):
        res = self.client.get(self.url, follow=True)
        self.assertNotContains(res, 'href="/favorites/"')
        self.assertNotContains(res, '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Documents')
        self.assertNotContains(res, 'href="/create/"')
        self.assertNotContains(res, 'href="/admin/"')

    def test_authenticated_user_navbar(self):
        self.client.login(username=self.user.email, password='pass')
        self.assertTrue(self.user.is_authenticated())

        res = self.client.get(self.url, follow=True)
        self.assertContains(res, 'href="/favorites/"')
        self.assertContains(res, '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Documents')
        self.assertNotContains(res, 'href="/create/"')
        self.assertNotContains(res, 'href="/admin/"')

    def test_document_controller_navbar(self):
        self.user.user_permissions = self.dc_perms
        self.user.save()
        self.client.login(username=self.user.email, password='pass')

        self.assertTrue(self.user.is_authenticated())
        self.assertTrue(self.user.has_perm('documents.add_document'))

        res = self.client.get(self.url, follow=True)
        self.assertContains(res, 'href="/favorites/"')
        self.assertContains(res, '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Documents')
        self.assertContains(res, 'href="/create/"')
        self.assertNotContains(res, 'href="/admin/"')

    def test_admin_navbar(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username=self.user.email, password='pass')
        self.assertTrue(self.user.is_authenticated())

        res = self.client.get(self.url, follow=True)
        self.assertContains(res, 'href="/favorites/"')
        self.assertContains(res, '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Documents')
        self.assertContains(res, 'href="/create/"')
        self.assertContains(res, 'href="/admin/"')


class AclTests(TestCase):

    def setUp(self):
        category = CategoryFactory()
        self.user = UserFactory(name='User', password='pass', category=category)
        self.home_url = reverse('category_document_list', args=[
            category.organisation.slug, category.slug
        ])
        self.create_url = reverse('document_create', args=[
            category.organisation.slug,
            category.slug
        ])
        self.login_url = '/accounts/login/'
        self.dc_perms = Permission.objects.filter(codename__endswith='_document')

    def test_anonymous_access(self):
        res = self.client.get(self.home_url)
        self.assertRedirects(res, '%s?next=%s' % (self.login_url, self.home_url))

        res = self.client.get(self.create_url)
        self.assertRedirects(res, '%s?next=%s' % (self.login_url, self.create_url))

    def test_authenticated_user_access(self):
        self.client.login(username=self.user.email, password='pass')

        res = self.client.get(self.home_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.create_url)
        self.assertRedirects(res, '%s?next=%s' % (self.login_url, self.create_url))

    def test_document_controller_access(self):
        self.user.user_permissions = self.dc_perms
        self.user.save()
        self.client.login(username=self.user.email, password='pass')

        res = self.client.get(self.home_url)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.create_url)
        self.assertEqual(res.status_code, 200)
