# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('categories', '0010_auto_20160202_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=250, verbose_name='Name')),
                ('approver', models.ForeignKey(related_name='related_lists_as_approver', verbose_name='Approver', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('categories', models.ManyToManyField(to='categories.Category', verbose_name='Category')),
                ('leader', models.ForeignKey(related_name='related_lists_as_leader', verbose_name='Leader', to=settings.AUTH_USER_MODEL)),
                ('reviewers', models.ManyToManyField(related_name='related_lists_as_reviewer', verbose_name='Reviewers', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Distribution list',
                'verbose_name_plural': 'Distribution lists',
            },
        ),
    ]
