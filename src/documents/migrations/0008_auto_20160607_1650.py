# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('documents', '0007_set_metadata_value'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'verbose_name': 'Document', 'verbose_name_plural': 'Documents', 'permissions': (('can_control_document', 'Can control document'), ('can_start_stop_review', 'Can start stop review'))},
        ),
        migrations.AddField(
            model_name='document',
            name='created_by',
            field=models.ForeignKey(related_name='documents_created', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Created by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
