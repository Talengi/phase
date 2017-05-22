# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='trigram',
            field=models.CharField(max_length=3, unique=True, null=True, verbose_name='Trigram'),
        ),
    ]
