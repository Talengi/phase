# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_auto_20151125_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='third_parties',
            field=models.ManyToManyField(related_name='linked_categories', to='accounts.Entity', blank=True),
        ),
    ]
