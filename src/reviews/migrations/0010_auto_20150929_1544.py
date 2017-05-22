# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0009_auto_20150928_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='received_date',
            field=models.DateField(null=True, verbose_name='Review received date', blank=True),
        ),
        migrations.AddField(
            model_name='review',
            name='revision_status',
            field=models.CharField(max_length=30, null=True, verbose_name='Revision status', blank=True),
        ),
        migrations.AddField(
            model_name='review',
            name='start_date',
            field=models.DateField(null=True, verbose_name='Review start date', blank=True),
        ),
    ]
