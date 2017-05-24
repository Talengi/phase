# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_entity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entity',
            options={'verbose_name': 'Entity', 'verbose_name_plural': 'Entities'},
        ),
        migrations.AddField(
            model_name='entity',
            name='trigram',
            field=models.CharField(default='   ', unique=True, max_length=3, verbose_name='Trigram'),
            preserve_default=False,
        ),
    ]
