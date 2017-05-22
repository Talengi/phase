# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transmittals', '0055_auto_20160303_1439'),
        ('default_documents', '0059_auto_20160225_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractordeliverablerevision',
            name='transmittals',
            field=models.ManyToManyField(related_name='default_documents_contractordeliverablerevision_related', verbose_name='transmittals', to='transmittals.OutgoingTransmittal'),
        ),
    ]
