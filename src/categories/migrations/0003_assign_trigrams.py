# -*- coding: utf-8 -*-


import random
import string

from django.db import migrations


def random_trigram():
    """Returns a word of three random letters."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(3))


def set_trigrams(app, schema_editor):
    Organisation = app.get_model('categories', 'Organisation')
    orgs = Organisation.objects.all()
    for org in orgs:
        org.trigram = random_trigram()
        org.save()


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_organisation_trigram'),
    ]

    operations = [
        migrations.RunPython(set_trigrams, migrations.RunPython.noop)
    ]
