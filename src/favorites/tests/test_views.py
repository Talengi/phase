from django.core.urlresolvers import reverse

from accounts.models import User
from documents.models import Document
from documents.tests.test_views import GenericViewTest
from favorites.models import Favorite


class FavoriteTest(GenericViewTest):
    url = reverse("favorite_list")

    def test_favorite_list(self):
        """
        Tests that a favorite list is accessible if logged in.
        """
        User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )

        # Logged in user
        auth = {'username': 'david', 'password': 'password'}
        self.assertGet(auth=auth)
        self.assertRendering('<p>You do not have any favorite document.</p>')

    def test_favorite_privacy(self):
        """
        Tests that a favorite is not shared accross users.
        """
        david = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        User.objects.create_user(
            'matthieu',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        favorite = Favorite.objects.create(
            document=document,
            user=david
        )

        # Right user
        auth = {'username': 'david', 'password': 'password'}
        self.assertGet(auth=auth)
        self.assertRendering('<td>%s</td>' % favorite.document.title)

        # Wrong user
        auth = {'username': 'matthieu', 'password': 'password'}
        self.assertGet(auth=auth)
        self.assertRendering('<p>You do not have any favorite document.</p>')

    def test_favorite_creation(self):
        """
        Tests that a favorite creation is possible.
        """
        user = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        self.url = reverse("favorite_create")
        self.assertPost({
            'document': document.id,
            'user': user.id,
        })
        # First favorite created
        self.assertEqual(self.content, '1')
        self.assertEqual(Favorite.objects.all().count(), 1)

    def test_favorite_deletion(self):
        """
        Tests that a favorite deletion is possible.
        """
        user = User.objects.create_user(
            'david',
            'foo@bar.fr',
            'password',
        )
        document = Document.objects.create(
            title=u'HAZOP report',
            current_revision_date='2012-04-20',
            sequencial_number="0004",
            discipline="HSE",
            document_type="REP",
            current_revision=u"03",
        )
        favorite = Favorite.objects.create(
            document=document,
            user=user
        )
        self.url = reverse("favorite_delete", args=[favorite.pk])
        self.assertPost(status_code=302)
        self.assertEqual(Favorite.objects.all().count(), 0)
