# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('url', models.CharField(max_length=200, verbose_name='Url')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='Created on')),
            ],
            options={
                'verbose_name': 'Bookmark',
                'verbose_name_plural': 'Bookmarks',
            },
        ),
    ]
