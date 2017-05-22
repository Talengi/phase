# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discussion', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='document',
            field=models.ForeignKey(verbose_name='Document', to='documents.Document'),
        ),
    ]
