# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0011_review_amended_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('approver', models.ForeignKey(related_name='related_lists_as_approver', verbose_name='Approver', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('leader', models.ForeignKey(related_name='related_lists_as_leader', verbose_name='Leader', to=settings.AUTH_USER_MODEL)),
                ('reviewers', models.ManyToManyField(related_name='related_lists_as_reviewer', verbose_name='Reviewers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Distribution list',
                'verbose_name_plural': 'Distribution lists',
            },
        ),
    ]
