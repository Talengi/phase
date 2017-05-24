# -*- coding: utf-8 -*-


from django.db import models, migrations
import metadata.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_review_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='return_code',
            field=metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Return code', list_index='REVIEW_RETURN_CODES', blank=True),
        ),
    ]
