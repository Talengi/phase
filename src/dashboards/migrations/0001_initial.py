# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings
import dashboards.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('slug', models.SlugField(max_length=250, verbose_name='Slug')),
                ('data_provider', dashboards.fields.DashboardProviderChoiceField(max_length=250, verbose_name='Dashboard data provider', choices=None)),
                ('authorized_users', models.ManyToManyField(related_name='dashboards', verbose_name='Authorized users', to=settings.AUTH_USER_MODEL, blank=True)),
                ('category', models.ForeignKey(verbose_name='Category', to='categories.Category')),
            ],
            options={
                'verbose_name': 'Dashboard',
                'verbose_name_plural': 'Dashboard provider',
            },
        ),
        migrations.AlterUniqueTogether(
            name='dashboard',
            unique_together=set([('slug', 'category')]),
        ),
    ]
