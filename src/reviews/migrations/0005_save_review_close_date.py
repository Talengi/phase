# -*- coding: utf-8 -*-


from django.db import migrations
from django.db.models import F
from django.utils import timezone


def set_closed_on(apps, schema_editor):
    Review = apps.get_model('reviews', 'Review')
    Review.objects \
        .exclude(reviewed_on=None) \
        .update(closed_on=F('reviewed_on'))

    Review.objects \
        .filter(reviewed_on=None) \
        .filter(closed=True) \
        .update(closed_on=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_review_closed_on'),
    ]

    operations = [
        migrations.RunPython(set_closed_on),
    ]
