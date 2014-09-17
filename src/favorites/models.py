from django.db import models

from accounts.models import User
from documents.models import Document


class Favorite(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document)
    last_view_date = models.DateTimeField(auto_now_add=True)

    def is_outdated(self):
        """Returns a boolean, True if the document has been updated."""
        return self.last_view_date < self.document.updated_on
