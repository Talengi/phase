# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0007_categorytemplate_use_create_form'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categorytemplate',
            old_name='use_create_form',
            new_name='use_creation_form',
        ),
    ]
