# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('description', models.CharField(max_length=200, null=True, verbose_name='Description', blank=True)),
                ('metadata_model', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Category template',
                'verbose_name_plural': 'Category templates',
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('description', models.CharField(max_length=200, null=True, verbose_name='Description', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='category_template',
            field=models.ForeignKey(verbose_name='Category template', to='categories.CategoryTemplate'),
        ),
        migrations.AddField(
            model_name='category',
            name='groups',
            field=models.ManyToManyField(to='auth.Group', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='organisation',
            field=models.ForeignKey(related_name='categories', verbose_name='Organisation', to='categories.Organisation'),
        ),
        migrations.AddField(
            model_name='category',
            name='users',
            field=models.ManyToManyField(related_name='categories', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('category_template', 'organisation')]),
        ),
    ]
