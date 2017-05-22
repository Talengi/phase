# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0008_auto_20151127_1124'),
        ('reviews', '0013_distributionlist_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributionlist',
            name='category',
        ),
        migrations.AddField(
            model_name='distributionlist',
            name='categories',
            field=models.ManyToManyField(to='categories.Category', verbose_name='Category'),
        ),
    ]
