# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151125_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_external',
            field=models.BooleanField(default=False, help_text='Used to tell apart regular users and externals ones (contractors', verbose_name='External User'),
        ),
    ]
