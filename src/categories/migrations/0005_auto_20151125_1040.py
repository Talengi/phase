# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('categories', '0004_auto_20151106_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='third_parties',
            field=models.ManyToManyField(related_name='linked_groups', to='auth.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='groups',
            field=models.ManyToManyField(related_name='owner_groups', to='auth.Group', blank=True),
        ),
    ]
