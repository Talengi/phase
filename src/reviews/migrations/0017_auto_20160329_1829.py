# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q


def check_distribution_liust(apps, schema):
    """ Check that distribution list users are not external."""
    DistributionList = apps.get_model('reviews', 'DistributionList')
    obj_to_fix = DistributionList.objects.filter(
        Q(leader__is_external=True) |
        Q(approver__is_external=True) |
        Q(reviewers__is_external=True))
    if obj_to_fix:
        message = 'At least one DistributionList document has an ' \
                  'user field set to external Users.' \
                  'Please correct that before applying this ' \
                  'migration: '
        print (message)
        raise ValueError("Incorrect field value")


class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0016_auto_20160209_1247'),
    ]

    operations = [
        migrations.RunPython(check_distribution_liust)
    ]
