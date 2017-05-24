# -*- coding: utf-8 -*-


from django.db import models, migrations
import metadata.fields


class Migration(migrations.Migration):

    dependencies = [
        ('default_documents', '0004_auto_20150812_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractordeliverablerevision',
            name='return_code',
            field=metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Return code', list_index='REVIEW_RETURN_CODES', blank=True),
        ),
        migrations.AlterField(
            model_name='demometadatarevision',
            name='return_code',
            field=metadata.fields.ConfigurableChoiceField(max_length=3, null=True, verbose_name='Return code', list_index='REVIEW_RETURN_CODES', blank=True),
        ),
    ]
