# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discussion', '0002_note_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='deleted_on',
            field=models.DateTimeField(null=True, verbose_name='Deleted on', blank=True),
        ),
    ]
