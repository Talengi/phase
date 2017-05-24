# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0005_auto_20160322_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='export_all_revisions',
            field=models.BooleanField(default=False, help_text='If False, only last revisions are included.', verbose_name='Export all revisions'),
        ),
    ]
