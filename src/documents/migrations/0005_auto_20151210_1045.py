# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_fill_document_numbers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_number',
            field=models.CharField(max_length=250, verbose_name='Document number'),
        ),
    ]
