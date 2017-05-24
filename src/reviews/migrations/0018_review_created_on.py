# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0017_auto_20160329_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='created_on',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Created on'),
        ),
    ]
