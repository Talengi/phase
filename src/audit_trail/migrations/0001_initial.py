# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actor_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('actor_object_str', models.CharField(max_length=254, null=True, verbose_name='Actor identifier', blank=True)),
                ('verb', models.CharField(default='joined', max_length=128, verbose_name='Verb', choices=[('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted'), ('joined', 'joined Phase')])),
                ('action_object_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('action_object_str', models.CharField(max_length=255, blank=True)),
                ('target_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('target_object_str', models.CharField(max_length=255, blank=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('action_object_content_type', models.ForeignKey(related_name='action_object', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor_content_type', models.ForeignKey(related_name='actor', blank=True, to='contenttypes.ContentType', null=True)),
                ('target_content_type', models.ForeignKey(related_name='target', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['-created_on'],
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
    ]
