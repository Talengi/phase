# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_last_login_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80, verbose_name='name')),
                ('type', models.CharField(default='contractor', max_length=80, verbose_name='Type', choices=[('contractor', 'Contractor'), ('supplier', 'Supplier'), ('other', 'Other')])),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users', blank=True)),
            ],
            options={
                'verbose_name': 'Entities',
            },
        ),
    ]
